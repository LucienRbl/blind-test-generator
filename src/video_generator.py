from pathlib import Path
from moviepy.editor import (
    VideoClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    concatenate_videoclips,
    AudioFileClip,
    ImageClip,
)
import numpy as np
import os
from typing import List, Tuple
import tempfile


from src.itunes_api import Track

DARK_BLUE_GRAY = (20, 20, 30)
LIGHT_BLUE = (100, 200, 255)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255, 255, 0)
CHARTREUSE = (127, 255, 0)
LIME = (0, 255, 0)
LIGHT_GREEN = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 128, 255)
DARK_BLUE = (0, 0, 255)
PURPLE = (127, 0, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 0, 127)


class VideoGenerator:
    """Class to generate vertical format blind test videos"""

    def __init__(self, width: int = 1080, height: int = 1920):
        """
        Initialize video generator

        Args:
            width: Video width (default: 1080 for vertical mobile format)
            height: Video height (default: 1920 for vertical mobile format)
        """
        self.width = width
        self.height = height
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(self.temp_dir, exist_ok=True)

        # Color scheme
        self.bg_color = DARK_BLUE_GRAY
        self.accent_color = LIGHT_BLUE
        self.text_color = WHITE

        self.font_path = Path(__file__).resolve().parent.parent / "assets" / "statics" / "fonts" / "JosefinSans-Medium.ttf"

        print("Font path:", self.font_path)
        print("Exists:", Path(self.font_path).exists())

    def create_wave_animation(self, duration: float) -> VideoClip:
        """Create simple animated wave overlay with background matching the main background"""
        bar_colors = [
            RED,
            ORANGE,
            YELLOW,
            CHARTREUSE,
            LIME,
            LIGHT_GREEN,
            CYAN,
            BLUE,
            DARK_BLUE,
            PURPLE,
            MAGENTA,
            PINK,
        ]

        def make_frame_rgb(t) -> np.ndarray:
            # Create RGB frame with background matching the main background
            frame = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)

            num_bars = 12
            bar_width = self.width // num_bars
            bar_spacing = 10
            bar_max_height = self.height // 3

            for i in range(num_bars):
                x_start = i * bar_width + bar_spacing
                x_end = (i + 1) * bar_width - bar_spacing

                bar_height = int(
                    (np.sin(2 * np.pi * (t * 0.5 + i / num_bars)) + 1)
                    / 2
                    * bar_max_height
                )

                y_start = self.height - bar_height - 100
                y_end = self.height - 100

                bar_color = bar_colors[i % len(bar_colors)]

                if x_start < x_end and y_start < y_end:
                    frame[y_start:y_end, x_start:x_end] = bar_color

            return frame

        # Create video clip with RGB frames
        video_clip = VideoClip(make_frame_rgb, duration=duration)

        return video_clip

    def create_text_clip(
        self,
        text: str,
        duration: float,
        fontsize: int = 80,
        position: Tuple[str, str] = ("center", "center"),
        color: Tuple[int, int, int] = None,
    ) -> TextClip:
        """Create a text clip with styling"""
        color = color or self.text_color

        return (
            TextClip(
                text,
                fontsize=fontsize,
                color=f"rgb({color[0]},{color[1]},{color[2]})",
                font=self.font_path,
                size=(self.width * 0.9, None),
                method="caption",
            )
            .set_duration(duration)
            .set_position(position)
        )

    def create_background_clip(
        self, duration: float, color: Tuple[int, int, int] = None
    ) -> ColorClip:
        """Create a colored background clip"""
        color = color or self.bg_color
        return ColorClip(size=(self.width, self.height), color=color, duration=duration)

    def create_pre_snippet_clip(
        self, track_number: int, duration: float = 2.0
    ) -> CompositeVideoClip:
        """Create countdown/transition clip for each track"""
        bg = self.create_background_clip(duration)

        # Main title
        title = self.create_text_clip(
            "Blind Test !",
            duration,
            fontsize=100,
            position=("center", 300),
            color=self.accent_color,
        )

        # Track number
        track_text = self.create_text_clip(
            f"Track #{track_number}",
            duration,
            fontsize=120,
            position=("center", "center"),
        )

        # Instructions
        instruction = self.create_text_clip(
            "Listen carefully...",
            duration,
            fontsize=60,
            position=("center", 1400),
        )

        return CompositeVideoClip([bg, title, track_text, instruction])

    def create_music_playing_clip(
        self, track_info: Track, track_number: int, duration: float
    ) -> CompositeVideoClip:
        """Create clip showing music is playing"""
        bg = self.create_background_clip(duration)  # Background
        wave = self.create_wave_animation(duration)  # Wave animation overlay

        # Title
        title = self.create_text_clip(
            f"Track #{track_number}",
            duration,
            fontsize=80,
            position=("center", 200),
            color=self.accent_color,
        )

        # Progress indicator
        countdown_clips = []
        for i in range(int(duration), 0, -1):  # 3→1 countdown
            count_clip = self.create_text_clip(
                str(i),
                duration=1,
                fontsize=120,
                position=("center", 800),
            )
            countdown_clips.append(count_clip)

        countdown = concatenate_videoclips(
            countdown_clips, method="compose"
        ).set_position(("center", 800))

        # Overlay the countdown only at the start (fade out)
        countdown = countdown.fadeout(0.5)

        return CompositeVideoClip([bg, wave, title, countdown])

    def create_answer_clip(
        self, duration: float, track_info: Track
    ) -> CompositeVideoClip:
        """Create answer clip showing artist and track name"""
        bg = self.create_background_clip(duration)

        answer_text = self.create_text_clip(
            f"{track_info.artist_name} - {track_info.track_name}",
            duration,
            fontsize=60,
            position=("center", 1050),
            color=self.text_color,
        )

        cover_image = (
            ImageClip(track_info.artwork_url)
            .set_duration(duration)
            .set_position(("center", 400))
        )

        return CompositeVideoClip([bg, answer_text, cover_image])

    def create_intro_clip(self, duration: float = 3.0) -> CompositeVideoClip:
        """Create intro clip for the blind test"""
        bg = self.create_background_clip(duration)

        title = self.create_text_clip(
            "MUSIC BLIND TEST",
            duration,
            fontsize=120,
            position=("center", 600),
            color=self.accent_color,
        )

        instructions = self.create_text_clip(
            "Can you guess the artist and song?",
            duration,
            fontsize=60,
            position=("center", 1200),
            color=(200, 200, 200),
        )

        return CompositeVideoClip([bg, title, instructions])

    def create_outro_clip(
        self, tracks_info: List[Track], duration: float = 10.0
    ) -> CompositeVideoClip:
        """Create outro clip with answers"""
        bg = self.create_background_clip(duration)

        title = self.create_text_clip(
            "Tanks for playing!",
            duration,
            fontsize=120,
            position=("center", 200),
            color=self.accent_color,
        )

        subtitle = self.create_text_clip(
            "How many did you guess correctly?",
            duration,
            fontsize=60,
            position=("center", 800),
            color=self.text_color,
        )

        return CompositeVideoClip([bg, title, subtitle])

    def generate_blind_test_video(
        self,
        audio_file: str,
        tracks_info: List[Track],
        output_path: str,
        snippet_duration: float = 15.0,
        pause_duration: float = 3.0,
        intro_duration: float = 3.0,
        outro_duration: float = 10.0,
        answer_duration: float = 4.0,
    ) -> bool:
        """
        Generate the complete blind test video

        Args:
            audio_file: Path to the complete audio file
            tracks_info: List of track information
            output_path: Output video file path
            snippet_duration: Duration of each music snippet
            pause_duration: Pause between tracks
            countdown_duration: Countdown before each track

        Returns:
            True if successful
        """
        try:
            video_clips = []
            current_time = 0

            # Load audio
            audio = AudioFileClip(audio_file)

            # Intro
            intro = self.create_intro_clip(intro_duration)
            video_clips.append(intro)
            current_time += intro_duration

            # Process each track
            for i, track_info in enumerate(tracks_info, 1):
                # Countdown clip
                countdown = self.create_pre_snippet_clip(i, pause_duration)
                video_clips.append(countdown)
                current_time += pause_duration

                # Music playing clip
                music_clip = self.create_music_playing_clip(
                    track_info, i, snippet_duration - answer_duration
                )
                video_clips.append(music_clip)
                current_time += snippet_duration - answer_duration

                # Answer clip
                answer_clip = self.create_answer_clip(answer_duration, track_info)
                video_clips.append(answer_clip)
                current_time += answer_duration

            outro = self.create_outro_clip(tracks_info, outro_duration)
            video_clips.append(outro)

            # Combine all video clips
            final_video = concatenate_videoclips(video_clips)

            # Set audio (trim to video length)
            final_audio = audio.subclip(0, min(audio.duration, final_video.duration))
            final_video = final_video.set_audio(final_audio)

            # Export video
            print(f"Exporting video to {output_path}...")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None,
                threads=4,
            )

            # Cleanup
            final_video.close()
            audio.close()

            print(f"✓ Video exported successfully: {output_path}")
            return True

        except Exception as e:
            print(f"Error generating video: {e}")
            return False

    def cleanup(self):
        """Clean up temporary files"""
        import shutil

        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

