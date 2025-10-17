# Blind Test Video Generator 🎵

A Python application that creates vertical format (TikTok-style) blind test videos using random music from the iTunes API and uploads them to YouTube.

## Features

- 🎵 Fetches random music tracks from iTunes API
- 🎬 Creates vertical format videos (1080x1920) perfect for mobile/TikTok
- 🔊 Processes audio with fade-in/fade-out effects
- 📱 Modern, clean video design with animated wave visualizer
- 🎯 Customizable track count, duration, and styling
- 🎨 Colorful animated bars that respond to music playback
- 📤 Optional automatic YouTube upload functionality

## Requirements

- Python 3.10+
- ffmpeg (for video processing)
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

## Installation

### Using uv (Recommended)

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone <your-repo-url>
cd blind-test
```

3. Install dependencies and setup the project:
```bash
uv sync
```
## Usage

Example command to generate a blind test video with 5 tracks and upload it to YouTube:
```bash
./blind-test-generator --upload --title "My Blind Test Video" --description "Can you guess the songs?" --num-tracks 5 --outro-duration 1
```
Use `--help` to see all available options:
```bash
./blind-test-generator --help
```

The application will:
1. Search for random tracks on iTunes
2. Download audio previews (few seconds each)
3. Create a complete blind test video with answers after each track.
4. Save everything to the `output/` directory
5. Optionally upload to YouTube if `--upload` is specified

### YouTube Upload
To enable YouTube uploads, you need to set up OAuth 2.0 credentials and store them in a `client_secrets.json` file in the project root. Follow the instructions in the [YouTube Data API documentation](https://developers.google.com/youtube/v3/getting-started) to create your credentials.


## Output Files

The application creates files in the `output/` directory:
- `blind_test_video_TIMESTAMP.mp4` - The complete video file
- `blind_test_audio_TIMESTAMP.wav` - Combined audio file


## Project Structure

```
blind-test/
├── src/
│   ├── blind_test_generator.py  # Main application entry point
│   ├── itunes_api.py           # iTunes API interface
│   ├── audio_processor.py      # Audio processing and effects
│   └── video_generator.py      # Video creation and effects
|   └── youtube_api.py          # YouTube API interface (if needed for uploads)
├── output/                     # Generated videos and audio
├── assets/                     # Static assets (fonts, images)
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```
   
## Customization

### Video Customization

Edit the `VideoGenerator` class in `src/video_generator.py` to customize:
- **Colors**: Modify the color constants at the top of the file
- **Fonts**: Change the font in the `create_text_clip` method
- **Animations**: Adjust the wave animation parameters
- **Layout**: Modify text positions and sizes

## Video Specifications

- **Resolution**: 1080x1920 (vertical format for mobile)
- **Frame Rate**: 24 FPS
- **Video Codec**: H.264 (MP4 container)
- **Audio Codec**: AAC
- **Duration**: ~86 seconds for 5 tracks (customizable)

## Development


### Adding New Features

1. **Audio Effects**: Modify `src/audio_processor.py`
2. **Video Effects**: Edit `src/video_generator.py`
3. **Music Sources**: Extend `src/itunes_api.py` or add new API integrations
4. **Main Logic**: Update `src/blind_test_generator.py`
5. **YouTube Upload**: Modify `src/youtube_api.py`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: 
   ```bash
   uv sync  # Reinstall dependencies
   ```

2. **ffmpeg not found**: 
   - Install ffmpeg for your system
   - Ensure it's in your system PATH

3. **No tracks found**: 
   - Check internet connection
   - Verify iTunes API availability
   - Try running again (API sometimes returns empty results)

4. **Video export fails**: 
   - Ensure ffmpeg is properly installed
   - Check available disk space
   - Verify write permissions in output directory

5. **YouTube upload errors**: 
   - Ensure `client_secrets.json` is correctly set up
   - Check OAuth 2.0 credentials and scopes
   - Review error messages for specific issues


## License

MIT License - Feel free to modify and distribute!
