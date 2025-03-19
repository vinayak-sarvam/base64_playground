# Base64 Audio Playground

A simple web application to convert and play base64-encoded audio strings.

## Features

- Convert base64 strings to playable audio
- Support for WAV and MP3 formats
- Simple, user-friendly interface
- Real-time error handling
- Clean URL management

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open in browser:
```
http://localhost:8000
```

## Usage

1. Select the audio format (WAV or MP3)
2. Paste your base64 audio string
3. Click "Convert & Play"
4. Use the audio player controls to play the sound

## Notes

- The base64 string should be a valid audio encoding
- Supports both raw base64 and data URL formats
- Automatically cleans up resources 