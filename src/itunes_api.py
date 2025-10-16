import requests
import random
from pydantic import BaseModel
from typing import List, Dict

class Track(BaseModel):
    track_name: str
    artist_name: str
    album_name: str
    preview_url: str
    artwork_url: str
    genre: str
    track_id: int
    duration: int  # in seconds

class iTunesAPI:
    """Class to interact with iTunes Search API for music discovery"""
    
    BASE_URL = "https://itunes.apple.com/search"
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_music(self, 
                    term: str = "", 
                    limit: int = 50, 
                    country: str = "US",
                    media: str = "music",
                    entity: str = "song") -> List[Track]:
        """
        Search for music using iTunes API
        
        Args:
            term: Search term (artist, song, etc.)
            limit: Number of results to return
            country: Country code for search
            media: Media type (music, movie, etc.)
            entity: Entity type (song, album, etc.)
            
        Returns:
            List of Track objects
        """
        params = {
            'term': term,
            'limit': limit,
            'country': country,
            'media': media,
            'entity': entity
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Filter results that have preview URLs and convert to Track objects
            tracks = []
            for track_data in data.get('results', []):
                if track_data.get('previewUrl') and track_data.get('trackName') and track_data.get('artistName'):
                    try:
                        track = Track(
                            track_name=track_data.get('trackName', 'Unknown'),
                            artist_name=track_data.get('artistName', 'Unknown Artist'),
                            album_name=track_data.get('collectionName', 'Unknown Album'),
                            preview_url=track_data.get('previewUrl'),
                            artwork_url=track_data.get('artworkUrl100', '').replace('100x100', '600x600'),
                            genre=track_data.get('primaryGenreName', 'Unknown'),
                            track_id=track_data.get('trackId', 0),
                            duration=track_data.get('trackTimeMillis', 30000) // 1000
                        )
                        tracks.append(track)
                    except Exception as e:
                        print(f"Error creating Track object: {e}")
                        continue
            
            return tracks
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching iTunes: {e}")
            return []
    
    def get_random_tracks(self, genres: List[str] = None, count: int = 5) -> List[Track]:
        """
        Get random tracks from different genres
        
        Args:
            genres: List of genres to search from
            count: Number of random tracks to return
            
        Returns:
            List of random Track objects
        """
        if not genres:
            genres = [
                "pop", "rock", "hip-hop", "electronic", "jazz", 
                "classical", "country", "reggae", "funk", "blues",
                "indie", "alternative", "dance", "r&b", "folk"
            ]
        
        all_tracks = []
        
        # Search for tracks in different genres
        for genre in random.sample(genres, min(len(genres), 5)):
            tracks = self.search_music(term=genre, limit=20)
            all_tracks.extend(tracks)
        
        # If we don't have enough tracks, search for popular terms
        if len(all_tracks) < count:
            popular_terms = ["love", "heart", "night", "time", "world", "life", "home"]
            for term in random.sample(popular_terms, 3):
                tracks = self.search_music(term=term, limit=15)
                all_tracks.extend(tracks)
        
        # Remove duplicates based on trackId
        unique_tracks = {}
        for track in all_tracks:
            if track.track_id and track.track_id not in unique_tracks:
                unique_tracks[track.track_id] = track
        
        track_list = list(unique_tracks.values())
        
        # Return random selection
        return random.sample(track_list, min(len(track_list), count))
    
    def download_preview(self, preview_url: str, filename: str) -> bool:
        """
        Download audio preview from iTunes
        
        Args:
            preview_url: URL of the audio preview
            filename: Local filename to save the audio
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            response = self.session.get(preview_url)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading preview: {e}")
            return False
    
