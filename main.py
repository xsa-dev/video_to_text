import os
import subprocess
from pathlib import Path

import assemblyai as aai
import toml


def load_config(config_path="config.toml"):
    """Load configuration settings from a TOML file."""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return toml.load(file)
    except FileNotFoundError:
        print(f"Error: configuration file {config_path} not found.")
        return None
    except Exception as exc:
        print(f"Error reading configuration: {exc}")
        return None


def extract_audio_from_video(video_path, output_audio_path, config):
    """Extract an audio track from a video file using ffmpeg."""
    try:
        audio_config = config.get("audio", {})
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            audio_config.get("codec", "pcm_s16le"),
            "-ar",
            str(audio_config.get("sample_rate", 16000)),
            "-ac",
            str(audio_config.get("channels", 1)),
            "-y",
            output_audio_path,
        ]

        print(f"      Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"      ffmpeg reported an error: {result.stderr}")
            return False

        if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0:
            print("      Audio file created successfully.")
            return True

        print("      Audio file was not created or is empty.")
        return False

    except Exception as exc:
        print(f"      Failed to extract audio: {exc}")
        return False


def transcribe_audio(audio_path, api_key, config):
    """Transcribe an audio file using the AssemblyAI API."""
    assemblyai_config = config.get("assemblyai", {})

    print(
        f"      AssemblyAI speech model: {assemblyai_config.get('speech_model', 'universal')}"
    )
    print(f"      Language code: {assemblyai_config.get('language', 'en')}")
    print(f"      Punctuation enabled: {assemblyai_config.get('punctuate', True)}")
    print(
        f"      Text formatting enabled: {assemblyai_config.get('format_text', True)}"
    )

    try:
        aai.settings.api_key = api_key

        config_obj = aai.TranscriptionConfig(
            speech_model=getattr(
                aai.SpeechModel, assemblyai_config.get("speech_model", "universal")
            ),
            language_code=assemblyai_config.get("language", "en"),
            punctuate=assemblyai_config.get("punctuate", True),
            format_text=assemblyai_config.get("format_text", True),
        )

        print("      Uploading audio for transcription...")
        print(f"      File: {audio_path}")

        transcriber = aai.Transcriber(config=config_obj)
        transcript = transcriber.transcribe(audio_path)

        print(f"      Transcription status: {transcript.status}")

        if transcript.status == "error":
            print(f"      Transcription failed: {transcript.error}")
            return None

        if transcript.status == "completed":
            print("      Transcription completed successfully.")
            print(f"      Transcript length: {len(transcript.text)} characters")
            return {"text": transcript.text, "status": transcript.status}

        print(f"      Transcription still in progress: {transcript.status}")
        return None

    except Exception as exc:
        print(f"      Error during transcription: {exc}")
        return None


def process_video_files(video_paths, api_key, config):
    """Process each video file: extract audio, transcribe, and save text."""
    total_files = len(video_paths)
    print(f"Processing {total_files} video file(s)...")
    print("=" * 60)

    for index, video_path in enumerate(video_paths, 1):
        print(f"\n[{index}/{total_files}] Processing: {os.path.basename(video_path)}")
        print(f"   Full path: {video_path}")

        if not os.path.exists(video_path):
            print(f"   ERROR: File not found: {video_path}")
            continue

        video_file = Path(video_path)
        audio_path = video_file.with_suffix(".wav")
        text_path = video_file.with_suffix(".txt")

        print(f"   Output audio file: {audio_path}")
        print(f"   Output transcript file: {text_path}")

        print("   Extracting audio from video...")
        if not extract_audio_from_video(video_path, str(audio_path), config):
            print(f"   ERROR: Failed to extract audio from {video_path}")
            continue
        print("   Audio extracted successfully.")

        audio_size = os.path.getsize(audio_path)
        print(f"   Audio file size: {audio_size / 1024 / 1024:.2f} MB")

        print("   Sending audio for transcription...")
        transcription_result = transcribe_audio(str(audio_path), api_key, config)

        if transcription_result:
            print("   Transcription received successfully.")
            if "text" in transcription_result:
                text_content = transcription_result["text"]
                text_length = len(text_content)
                print(f"   Transcript length: {text_length} characters")

                with open(text_path, "w", encoding="utf-8") as file:
                    file.write(text_content)
                print(f"   Transcript saved to: {text_path}")

                preview = text_content[:100].replace("\n", " ")
                if len(text_content) > 100:
                    preview += "..."
                print(f"   Transcript preview: {preview}")
            else:
                print(f"   ERROR: Unexpected API response: {transcription_result}")
        else:
            print(f"   ERROR: Failed to transcribe {video_path}")

        if os.path.exists(audio_path):
            os.remove(audio_path)
            print("   Temporary audio file removed.")

        print(f"   Completed processing {os.path.basename(video_path)}.")
        print("-" * 60)


def main():
    config = load_config()
    if not config:
        return

    video_paths = config.get("video", {}).get("paths", [])
    if not video_paths:
        print("Error: no video paths found in the configuration.")
        return

    api_key_from_env = os.environ.get("ASSEMBLYAI_API_KEY")
    api_key_from_config = config.get("assemblyai", {}).get("api_key")
    api_key = api_key_from_env or api_key_from_config

    if not api_key:
        print("Error: AssemblyAI API key not provided.")
        print("Set the API key via an environment variable:")
        print("    export ASSEMBLYAI_API_KEY='your_api_key_here'")
        print("or add it to the [assemblyai] section in config.toml.")
        return

    source = "environment variable" if api_key_from_env else "config file"
    print(f"Using AssemblyAI API key from {source}.")

    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg not found. Install ffmpeg to extract audio.")
        return

    process_video_files(video_paths, api_key, config)
    print("Processing completed.")


if __name__ == "__main__":
    main()
