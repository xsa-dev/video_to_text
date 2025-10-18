# Video to Text Converter

A simple utility that extracts audio tracks from video files, sends them to AssemblyAI for transcription, and saves the resulting text alongside each source video.

## Installation

1. Install the Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install ffmpeg (required for audio extraction):
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

3. Provide your AssemblyAI API key using one of the following methods:
```bash
# Preferred: environment variable
export ASSEMBLYAI_API_KEY="your_api_key_here"

# Optional: add api_key to the [assemblyai] section in config.toml
```

## Configuration

All settings live in `config.toml`:

- `video.paths` — list of absolute or relative paths to the video files to process
- `assemblyai` — AssemblyAI related options (API key, speech model, language, formatting)
- `audio` — audio extraction parameters (sample rate, channels, codec)

### Example configuration

```toml
[video]
paths = [
    "/path/to/video1.mp4",
    "/path/to/video2.mp4"
]

[assemblyai]
# Leave blank to rely on ASSEMBLYAI_API_KEY
api_key = ""
speech_model = "universal"
language = "en"
punctuate = true
format_text = true

[audio]
sample_rate = 16000
channels = 1
codec = "pcm_s16le"
```

## Usage

1. Obtain an API key from [AssemblyAI](https://www.assemblyai.com/).
2. Update `config.toml` with video paths and any preferred transcription options.
3. Export `ASSEMBLYAI_API_KEY` (or set the key in the config file).
4. Run the script:
```bash
python main.py
```

## What the script does

1. Loads configuration from `config.toml`.
2. Extracts audio from each video file to WAV (16 kHz, mono).
3. Sends the audio to AssemblyAI for transcription.
4. Saves the transcript to a `.txt` file next to the source video.
5. Removes temporary audio files once transcription completes.

## Output format

For each video file `video.mp4`, the script creates a paired transcript file `video.txt`.
