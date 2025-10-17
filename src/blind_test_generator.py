#!/usr/bin/env python3
"""
Blind Test Video Generator
Creates a vertical format (TikTok-style) blind test video using random music from iTunes API
"""

import os
import argparse
from datetime import datetime

from src.itunes_api import iTunesAPI
from src.audio_processor import AudioProcessor
from src.video_generator import VideoGenerator
from src.youtube_api import YouTubeAPI


def main(
    num_tracks: int = 5,
    snippet_duration: int = 10,
    pause_duration: int = 2,
    intro_duration: int = 1,
    outro_duration: int = 1,
    answer_duration: int = 4,
    upload: bool = False,
    title: str = "Blind Test Video",
    description: str = "Enjoy this blind test video!",
):
    """Main function to create blind test video"""

    print("🎵 Blind Test Video Generator 🎵")
    print("=" * 50)
    video_duration = num_tracks * (snippet_duration + pause_duration) + intro_duration + outro_duration 
    print(f"ℹ️  Estimated video duration: {video_duration} seconds")
    if video_duration > 60:
        print(
            f"⚠️  Warning: The total video duration ({video_duration} seconds) may exceed typical short video limits (e.g., 60 seconds)."
        )
        input("Press Enter to continue...")

    # Create output directory
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "output"
    )
    os.makedirs(output_dir, exist_ok=True)

    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize components
    print("🔧 Initializing components...")
    itunes = iTunesAPI()
    audio_processor = AudioProcessor()
    video_generator = VideoGenerator()

    try:
        # Step 1: Get random tracks from iTunes
        print(f"🎵 Searching for {num_tracks} random tracks...")
        tracks_info = itunes.get_random_tracks(count=num_tracks)

        if not tracks_info:
            print("❌ No tracks found! Please check your internet connection.")
            return False

        # Process track information
        print(f"✓ Found {len(tracks_info)} tracks:")
        for i, track in enumerate(tracks_info, 1):
            print(f"  {i}. {track.artist_name} - {track.track_name} ({track.genre})")

        # Step 2: Create audio for blind test
        print("\n🔊 Creating audio for blind test...")
        complete_audio, processed_tracks = audio_processor.create_blind_test_audio(
            tracks_info,
            snippet_duration=snippet_duration,
            pause_duration=pause_duration,
            intro_duration=intro_duration
        )

        if not processed_tracks:
            print("❌ No audio tracks were processed successfully!")
            return False

        # Save audio file
        audio_filename = f"blind_test_audio_{timestamp}.wav"
        audio_path = os.path.join(output_dir, audio_filename)

        print(f"💾 Saving audio to {audio_path}...")
        if not audio_processor.save_audio(complete_audio, audio_path):
            print("❌ Failed to save audio file!")
            return False

        print(f"✓ Audio saved: {len(complete_audio) / 1000:.1f} seconds")

        # Step 3: Create video
        print("\n🎬 Creating video...")
        video_filename = f"blind_test_video_{timestamp}.mp4"
        video_path = os.path.join(output_dir, video_filename)

        video_generation_success = video_generator.generate_blind_test_video(
            audio_file=audio_path,
            tracks_info=processed_tracks,
            output_path=video_path,
            snippet_duration=snippet_duration,
            pause_duration=pause_duration,
            intro_duration=intro_duration,
            outro_duration=outro_duration,
            answer_duration=answer_duration,
        )

        if video_generation_success:
            print("\n🎉 Success! Blind test video created:")
            print(f"   📹 Video: {video_path}")
            print(f"   🔊 Audio: {audio_path}")
            print("\n📋 Tracks in the blind test:")
            for i, track in enumerate(processed_tracks, 1):
                print(f"   {i}- {track.track_name}")

            if upload:
                try:
                    # Step 4: Upload to YouTube
                    print("\n🚀 Uploading video to YouTube...")
                    youtube_api = YouTubeAPI("client_secret.json")
                    youtube_api.upload_video(
                        file=video_path,
                        title=title,
                        description=description,
                        tags=["blind test", "music quiz", "fun", "challenge", "#short"],
                        category="24",  # Entertainment
                        privacyStatus="public",
                    )
                    print("✅ Video uploaded successfully!")
                except Exception as e:
                    print(f"❌ Video upload failed: {e}")
            return True
        else:
            print("❌ Failed to create video!")
            return False

    except KeyboardInterrupt:
        print("\\n⏹️  Operation cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        print("🧹 Cleaning up temporary files...")
        audio_processor.cleanup()
        video_generator.cleanup()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Generate a blind test video")

    argparser.add_argument(
        "--output-dir", help="Directory to save the output files", default="output"
    )
    argparser.add_argument(
        "--num-tracks", type=int, help="Number of tracks in the blind test", default=4
    )
    argparser.add_argument(
        "--snippet-duration",
        type=int,
        help="Duration of each snippet in seconds",
        default=12,
    )
    argparser.add_argument(
        "--pause-duration",
        type=int,
        help="Duration of pause between snippets in seconds",
        default=1,
    )
    argparser.add_argument(
        "--intro-duration", type=int, help="Duration of intro in seconds", default=5
    )
    argparser.add_argument(
        "--outro-duration", type=int, help="Duration of outro in seconds", default=2
    )
    argparser.add_argument(
        "--answer-duration",
        type=int,
        help="Duration of answer reveal in seconds",
        default=2,
    )

    argparser.add_argument(
        "--upload", action="store_true", help="Upload the generated video to YouTube"
    )
    argparser.add_argument(
        "--title", help="Title for the YouTube video", default="Blind Test Video"
    )
    argparser.add_argument(
        "--description",
        help="Description for the YouTube video",
        default="Enjoy this blind test video!",
    )

    args = argparser.parse_args()

    main(
        num_tracks=args.num_tracks,
        snippet_duration=args.snippet_duration,
        pause_duration=args.pause_duration,
        intro_duration=args.intro_duration,
        outro_duration=args.outro_duration,
        answer_duration=args.answer_duration,
        upload=args.upload,
        title=args.title,
        description=args.description,
    )
