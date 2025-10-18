# Video to Text Converter

A simple utility that extracts audio tracks from video files and transcribes them using either AssemblyAI API or whisper-cli, saving the resulting text alongside each source video.

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

3. Choose your transcription method:

### Option A: Using whisper-cli (Recommended)
1. Install whisper-cli:
```bash
# macOS
brew install whisper-cli

# Or build from source: https://github.com/ggerganov/whisper.cpp
```

2. Download a whisper model (e.g., ggml-large-v3-turbo.bin) and place it in the project directory.

### Option B: Using AssemblyAI API
1. Provide your AssemblyAI API key using one of the following methods:
```bash
# Preferred: environment variable
export ASSEMBLYAI_API_KEY="your_api_key_here"

# Optional: add api_key to the [assemblyai] section in config.toml
```

## Configuration

All settings live in `config.toml`:

- `video.paths` — list of absolute or relative paths to the video files to process
- `transcription.method` — choose between "whisper" or "assemblyai"
- `whisper` — whisper-cli related options (model path, language, threads, etc.)
- `assemblyai` — AssemblyAI related options (API key, speech model, language, formatting)
- `audio` — audio extraction parameters (sample rate, channels, codec)

### Example configuration

```toml
[video]
paths = [
    "/path/to/video1.mp4",
    "/path/to/video2.mp4"
]

[transcription]
# Method: "whisper" or "assemblyai"
method = "whisper"

[whisper]
# Path to the whisper model file
model_path = "ggml-large-v3-turbo.bin"
# Language code (e.g., "ru", "en", "auto")
language = "ru"
# Number of threads
threads = 16
# Suppress non-speech tokens
suppress_nst = true
# Max context
max_context = 128
# No prompt
no_prompt = true
# Best of N
best_of = 7

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

1. Update `config.toml` with video paths and your preferred transcription method.
2. If using AssemblyAI, obtain an API key from [AssemblyAI](https://www.assemblyai.com/) and set it as an environment variable or in the config file.
3. If using whisper-cli, ensure the model file is in the project directory.
4. Run the script:
```bash
python main.py
```

## What the script does

1. Loads configuration from `config.toml`.
2. Extracts audio from each video file to WAV (16 kHz, mono).
3. Transcribes the audio using the selected method (whisper-cli or AssemblyAI).
4. Saves the transcript to a `.txt` file next to the source video.
5. Removes temporary audio files once transcription completes.

## Output format

For each video file `video.mp4`, the script creates a paired transcript file `video.txt`.
