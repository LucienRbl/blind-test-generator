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

def main():
    """Main function to create blind test video"""
    
    print("🎵 Blind Test Video Generator 🎵")
    print("=" * 50)
    
    # Configuration
    num_tracks = 5          # Number of tracks in the blind test
    snippet_duration = 15   # Duration of each music snippet in seconds
    pause_duration = 2      # Duration of pause between snippets in seconds
    intro_duration = 1      # Duration of intro silence in seconds
    outro_duration = 3      # Duration of outro silence in seconds
    answer_duration = 4     # Duration to show answers at the end of snippet in seconds
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
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
            intro_duration=intro_duration,
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
        
        print(f"✓ Audio saved: {len(complete_audio)/1000:.1f} seconds")
        
        # Step 3: Create video
        print("\n🎬 Creating video...")
        video_filename = f"blind_test_video_{timestamp}.mp4"
        video_path = os.path.join(output_dir, video_filename)
        
        success = video_generator.generate_blind_test_video(
            audio_file=audio_path,
            tracks_info=processed_tracks,
            output_path=video_path,
            snippet_duration=snippet_duration,
            pause_duration=pause_duration,
            intro_duration=intro_duration,
            outro_duration=outro_duration,
            answer_duration=answer_duration
        )
        
        if success:
            print("\n🎉 Success! Blind test video created:")
            print(f"   📹 Video: {video_path}")
            print(f"   🔊 Audio: {audio_path}")
            print("\n📋 Tracks in the blind test:")
            for i, track in enumerate(processed_tracks, 1):
                print(f"   {i}- {track.track_name}")

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
    parser = argparse.ArgumentParser(description="Generate a blind test video")
    
    args = parser.parse_args()
    
    main()
