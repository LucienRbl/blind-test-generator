import os
import requests
from pydub import AudioSegment
from pydub.effects import normalize
from typing import List, Dict, Tuple
import tempfile
import random

from src.itunes_api import Track

class AudioProcessor:
    """Class to handle audio processing for blind test videos"""
    
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def download_audio(self, url: str, filename: str) -> bool:
        """
        Download audio file from URL
        
        Args:
            url: URL of the audio file
            filename: Local filename to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"Error downloading audio from {url}: {e}")
            return False
    
    def process_audio_snippet(self, 
                            filepath: str, 
                            duration: int = 15, 
                            fade_duration: int = 2) -> AudioSegment:
        """
        Process audio snippet for blind test
        
        Args:
            filepath: Path to audio file
            duration: Duration of snippet in seconds
            fade_duration: Fade in/out duration in seconds
            
        Returns:
            Processed AudioSegment
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(filepath)
            
            # Normalize audio
            audio = normalize(audio)
            
            # Get random start position (avoid first and last 10 seconds)
            audio_length = len(audio) / 1000  # Convert to seconds
            if audio_length > duration + 20:  # Ensure enough content
                start_time = random.uniform(10, audio_length - duration - 10)
            else:
                start_time = 0
            
            # Extract snippet
            start_ms = int(start_time * 1000)
            end_ms = int((start_time + duration) * 1000)
            snippet = audio[start_ms:end_ms]
            
            # Apply fade in/out
            fade_ms = fade_duration * 1000
            snippet = snippet.fade_in(fade_ms).fade_out(fade_ms)
            
            return snippet
            
        except Exception as e:
            print(f"Error processing audio {filepath}: {e}")
            return None
    
    def create_silence(self, duration: int) -> AudioSegment:
        """Create silence segment"""
        return AudioSegment.silent(duration=duration * 1000)
    
    def create_blind_test_audio(self, 
                              tracks_info: List[Dict],
                              snippet_duration: int = 15,
                              pause_duration: int = 3,
                              intro_duration: int = 2) -> Tuple[AudioSegment, List[Track]]:
        """
        Create complete blind test audio with all snippets
        
        Args:
            tracks_info: List of track information dictionaries
            snippet_duration: Duration of each music snippet
            pause_duration: Duration of pause before each snippet
            intro_duration: Duration of intro silence 
            
        Returns:
            Tuple of (complete audio, processed tracks info)
        """
        audio_segments = []
        processed_tracks = []
        
        print(f"Creating blind test with {len(tracks_info)} tracks...")
        
        for i, track_info in enumerate(tracks_info):
            print(f"Processing track {i+1}: {track_info.artist_name} - {track_info.track_name}")
            
            # Download audio
            filename = f"track_{i+1}_{track_info.track_id}.m4a"
            filepath = os.path.join(self.temp_dir, filename)

            if self.download_audio(track_info.preview_url, filename):
                # Process audio snippet
                snippet = self.process_audio_snippet(filepath, snippet_duration)
                
                if snippet:
                    # Add countdown/intro silence
                    if i == 0:  # No silence before first track
                        audio_segments.append(self.create_silence(intro_duration))
                    
                    # Add pause before snippet
                    audio_segments.append(self.create_silence(pause_duration))
                    # Add the music snippet
                    audio_segments.append(snippet)
                    
                    
                    # Store processed track info
                    # track_info = sum(len(seg) for seg in audio_segments[:-1]) / 1000
                    # track_info['snippet_duration'] = len(snippet) / 1000
                    processed_tracks.append(track_info)
                    
                    print(f"✓ Successfully processed track {i+1}")
                else:
                    print(f"✗ Failed to process audio for track {i+1}")
            else:
                print(f"✗ Failed to download track {i+1}")
        
        if audio_segments:
            # Combine all segments
            complete_audio = sum(audio_segments, AudioSegment.empty())
            print(f"Complete audio duration: {len(complete_audio) / 1000:.1f} seconds")
            return complete_audio, processed_tracks
        else:
            print("No audio segments created!")
            return AudioSegment.empty(), []
    
    def save_audio(self, audio: AudioSegment, output_path: str) -> bool:
        """
        Save audio to file
        
        Args:
            audio: AudioSegment to save
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            audio.export(output_path, format="wav")
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

