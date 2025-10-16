# Blind Test Video Generator 🎵

A Python application that creates vertical format (TikTok-style) blind test videos using random music from the iTunes API.

## Features

- 🎵 Fetches random music tracks from iTunes API
- 🎬 Creates vertical format videos (1080x1920) perfect for mobile/TikTok
- 🔊 Processes audio with fade-in/fade-out effects
- 📱 Modern, clean video design with animated wave visualizer
- 🎯 Customizable track count, duration, and styling
- 🎨 Colorful animated bars that respond to music playback

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

### Using uv (Recommended)
```bash
uv run blind-test

```

The application will:
1. Search for 5 random tracks on iTunes
2. Download audio previews (few seconds each)
3. Create a complete blind test video with answers after each track.
4. Save everything to the `output/` directory

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
├── output/                     # Generated videos and audio
├── assets/                     # Static assets (fonts, images)
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## Customization

You can customize the blind test by modifying the parameters in `src/blind_test_generator.py`:

```python
def main():
    num_tracks = 5              # Number of tracks
    snippet_duration = 15.0     # Length of each snippet (seconds)
    pause_duration = 3.0        # Pause between tracks (seconds)
    intro_duration = 3.0        # Intro screen duration (seconds)
    outro_duration = 10.0       # Outro screen duration (seconds)
    answer_duration = 4.0       # Answer reveal duration (seconds)
```

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

### Running in Development Mode

```bash
# Install in development mode
uv sync

# Run the application
uv run blind-test
```

### Adding New Features

1. **Audio Effects**: Modify `src/audio_processor.py`
2. **Video Effects**: Edit `src/video_generator.py`
3. **Music Sources**: Extend `src/itunes_api.py` or add new API integrations
4. **Main Logic**: Update `src/blind_test_generator.py`

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

5. **Import errors after changes**:
   ```bash
   uv sync  # Refresh the package installation
   ```

## License

MIT License - Feel free to modify and distribute!
