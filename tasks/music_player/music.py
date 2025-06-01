# tasks/music/music_controller.py

import os
import json
import random
import time
from typing import List, Dict, Any, Optional, Tuple
import sqlite3
import datetime

class MusicController:
    def __init__(self):
        # Create database for music library if it doesn't exist
        self.db_path = os.path.join(os.path.dirname(__file__), "music_library.db")
        self.initialize_db()
        self.current_playlist = []
        self.current_song = None
        self.is_playing = False
        self.volume = 70  # Default volume level (0-100)
        self.repeat_mode = "off"  # off, song, playlist
        self.shuffle_mode = False

    def initialize_db(self):
        """Initialize the music database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create songs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            genre TEXT,
            path TEXT,
            duration INTEGER,
            play_count INTEGER DEFAULT 0,
            last_played TIMESTAMP,
            rating INTEGER DEFAULT 0,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create playlists table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create playlist_songs table (for many-to-many relationship)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist_songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            song_id INTEGER,
            position INTEGER,
            FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()

    def add_song(self, title: str, artist: str, album: str = None, 
                 genre: str = None, path: str = None, duration: int = 0) -> Tuple[bool, str]:
        """Add a song to the music library"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if song already exists
            cursor.execute("SELECT id FROM songs WHERE title = ? AND artist = ?", (title, artist))
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                return False, f"Song '{title}' by {artist} already exists in the library"
            
            # Add new song
            cursor.execute(
                "INSERT INTO songs (title, artist, album, genre, path, duration) VALUES (?, ?, ?, ?, ?, ?)",
                (title, artist, album, genre, path, duration)
            )
            
            conn.commit()
            song_id = cursor.lastrowid
            conn.close()
            
            return True, f"Added '{title}' by {artist} to the music library (ID: {song_id})"
        except Exception as e:
            return False, f"Failed to add song: {str(e)}"

    def search_songs(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for songs in the music library"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search in title, artist, album, and genre
            search_term = f"%{query}%"
            cursor.execute(
                """SELECT * FROM songs 
                WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR genre LIKE ?
                ORDER BY play_count DESC LIMIT ?""",
                (search_term, search_term, search_term, search_term, limit)
            )
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
        except Exception as e:
            print(f"Error searching songs: {e}")
            return []

    def create_playlist(self, name: str) -> Tuple[bool, str]:
        """Create a new playlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if playlist already exists
            cursor.execute("SELECT id FROM playlists WHERE name = ?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                return False, f"Playlist '{name}' already exists"
            
            # Create new playlist
            cursor.execute(
                "INSERT INTO playlists (name) VALUES (?)",
                (name,)
            )
            
            conn.commit()
            playlist_id = cursor.lastrowid
            conn.close()
            
            return True, f"Created playlist '{name}' (ID: {playlist_id})"
        except Exception as e:
            return False, f"Failed to create playlist: {str(e)}"

    def add_song_to_playlist(self, playlist_name: str, song_id: int) -> Tuple[bool, str]:
        """Add a song to a playlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get playlist ID
            cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
            playlist_result = cursor.fetchone()
            
            if not playlist_result:
                conn.close()
                return False, f"Playlist '{playlist_name}' not found"
            
            playlist_id = playlist_result[0]
            
            # Check if song exists
            cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (song_id,))
            song_result = cursor.fetchone()
            
            if not song_result:
                conn.close()
                return False, f"Song with ID {song_id} not found"
            
            song_title, song_artist = song_result
            
            # Check if song is already in the playlist
            cursor.execute(
                "SELECT id FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
                (playlist_id, song_id)
            )
            
            if cursor.fetchone():
                conn.close()
                return False, f"Song '{song_title}' is already in playlist '{playlist_name}'"
            
            # Get the next position in the playlist
            cursor.execute(
                "SELECT COALESCE(MAX(position), 0) FROM playlist_songs WHERE playlist_id = ?",
                (playlist_id,)
            )
            next_position = cursor.fetchone()[0] + 1
            
            # Add song to playlist
            cursor.execute(
                "INSERT INTO playlist_songs (playlist_id, song_id, position) VALUES (?, ?, ?)",
                (playlist_id, song_id, next_position)
            )
            
            # Update playlist last_modified timestamp
            cursor.execute(
                "UPDATE playlists SET last_modified = CURRENT_TIMESTAMP WHERE id = ?",
                (playlist_id,)
            )
            
            conn.commit()
            conn.close()
            
            return True, f"Added '{song_title}' by {song_artist} to playlist '{playlist_name}'"
        except Exception as e:
            return False, f"Failed to add song to playlist: {str(e)}"

    def list_playlists(self) -> List[Dict[str, Any]]:
        """List all playlists"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT p.id, p.name, p.created_date, p.last_modified, 
                COUNT(ps.id) as song_count
                FROM playlists p
                LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
                GROUP BY p.id
                ORDER BY p.name"""
            )
            
            playlists = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return playlists
        except Exception as e:
            print(f"Error listing playlists: {e}")
            return []

    def get_playlist_songs(self, playlist_name: str) -> List[Dict[str, Any]]:
        """Get all songs in a playlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT s.id, s.title, s.artist, s.album, s.genre, s.duration, ps.position
                FROM songs s
                JOIN playlist_songs ps ON s.id = ps.song_id
                JOIN playlists p ON ps.playlist_id = p.id
                WHERE p.name = ?
                ORDER BY ps.position""",
                (playlist_name,)
            )
            
            songs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return songs
        except Exception as e:
            print(f"Error getting playlist songs: {e}")
            return []

    def play_song(self, song_id: int) -> Tuple[bool, str]:
        """Play a specific song (simulation)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get song details
            cursor.execute("SELECT id, title, artist, path FROM songs WHERE id = ?", (song_id,))
            song = cursor.fetchone()
            
            if not song:
                conn.close()
                return False, f"Song with ID {song_id} not found"
            
            song_id, title, artist, path = song
            
            # Update play count and last played
            cursor.execute(
                "UPDATE songs SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP WHERE id = ?",
                (song_id,)
            )
            
            conn.commit()
            conn.close()
            
            # In a real implementation, this would start the actual music playback
            self.current_song = {"id": song_id, "title": title, "artist": artist, "path": path}
            self.is_playing = True
            
            return True, f"Now playing: '{title}' by {artist}"
        except Exception as e:
            return False, f"Failed to play song: {str(e)}"

    def play_playlist(self, playlist_name: str, shuffle: bool = False) -> Tuple[bool, str]:
        """Load and play a playlist"""
        try:
            # Get playlist songs
            playlist_songs = self.get_playlist_songs(playlist_name)
            
            if not playlist_songs:
                return False, f"Playlist '{playlist_name}' is empty or doesn't exist"
            
            # Set current playlist
            self.current_playlist = playlist_songs
            self.shuffle_mode = shuffle
            
            # If shuffle is enabled, randomize the playlist
            if shuffle:
                random.shuffle(self.current_playlist)
            
            # Play the first song
            first_song = self.current_playlist[0]
            success, message = self.play_song(first_song["id"])
            
            if success:
                return True, f"Playing playlist '{playlist_name}' ({len(playlist_songs)} songs)"
            else:
                return False, message
        except Exception as e:
            return False, f"Failed to play playlist: {str(e)}"

    def pause(self) -> Tuple[bool, str]:
        """Pause the current playback"""
        if not self.current_song:
            return False, "No song is currently playing"
        
        if not self.is_playing:
            return False, "Playback is already paused"
        
        # In a real implementation, this would pause the actual music playback
        self.is_playing = False
        return True, f"Paused '{self.current_song['title']}'"

    def resume(self) -> Tuple[bool, str]:
        """Resume the current playback"""
        if not self.current_song:
            return False, "No song loaded to resume"
        
        if self.is_playing:
            return False, "Already playing"
        
        # In a real implementation, this would resume the actual music playback
        self.is_playing = True
        return True, f"Resumed '{self.current_song['title']}'"

    def stop(self) -> Tuple[bool, str]:
        """Stop the current playback"""
        if not self.current_song:
            return False, "No song is currently playing"
        
        # In a real implementation, this would stop the actual music playback
        song_info = self.current_song
        self.current_song = None
        self.is_playing = False
        return True, f"Stopped playing '{song_info['title']}'"

    def next_song(self) -> Tuple[bool, str]:
        """Play the next song in the playlist"""
        if not self.current_playlist:
            return False, "No active playlist"
        
        if not self.current_song:
            # If no song is playing, play the first one
            return self.play_playlist(self.current_playlist[0]["playlist_name"])
        
        # Find the current song in the playlist
        current_id = self.current_song["id"]
        current_index = -1
        
        for i, song in enumerate(self.current_playlist):
            if song["id"] == current_id:
                current_index = i
                break
        
        if current_index == -1 or current_index == len(self.current_playlist) - 1:
            # At the end of playlist or song not in playlist
            if self.repeat_mode == "playlist":
                # If repeat playlist, go back to the first song
                return self.play_song(self.current_playlist[0]["id"])
            else:
                return False, "End of playlist reached"
        
        # Play the next song
        next_song = self.current_playlist[current_index + 1]
        return self.play_song(next_song["id"])

    def previous_song(self) -> Tuple[bool, str]:
        """Play the previous song in the playlist"""
        if not self.current_playlist:
            return False, "No active playlist"
        
        if not self.current_song:
            # If no song is playing, play the first one
            return self.play_playlist(self.current_playlist[0]["playlist_name"])
        
        # Find the current song in the playlist
        current_id = self.current_song["id"]
        current_index = -1
        
        for i, song in enumerate(self.current_playlist):
            if song["id"] == current_id:
                current_index = i
                break
        
        if current_index <= 0:
            # At the beginning of playlist or song not in playlist
            if self.repeat_mode == "playlist":
                # If repeat playlist, go to the last song
                return self.play_song(self.current_playlist[-1]["id"])
            else:
                return False, "Beginning of playlist reached"
        
        # Play the previous song
        prev_song = self.current_playlist[current_index - 1]
        return self.play_song(prev_song["id"])

    def set_volume(self, level: int) -> Tuple[bool, str]:
        """Set the volume level (0-100)"""
        if not 0 <= level <= 100:
            return False, "Volume level must be between 0 and 100"
        
        # In a real implementation, this would set the actual volume
        self.volume = level
        return True, f"Volume set to {level}%"

    def toggle_shuffle(self) -> Tuple[bool, str]:
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        
        if self.shuffle_mode:
            # If current playlist exists, shuffle it
            if self.current_playlist:
                current_song_id = self.current_song["id"] if self.current_song else None
                
                # Remove current song from shuffle
                shuffled_playlist = [song for song in self.current_playlist if song["id"] != current_song_id]
                random.shuffle(shuffled_playlist)
                
                # Put current song at the beginning if it exists
                if current_song_id:
                    current_song = next(song for song in self.current_playlist if song["id"] == current_song_id)
                    self.current_playlist = [current_song] + shuffled_playlist
                else:
                    self.current_playlist = shuffled_playlist
            
            return True, "Shuffle mode enabled"
        else:
            # If we disable shuffle, restore original order if possible
            # For a real implementation, we would need to store the original order
            return True, "Shuffle mode disabled"

    def set_repeat_mode(self, mode: str) -> Tuple[bool, str]:
        """Set repeat mode (off, song, playlist)"""
        valid_modes = ["off", "song", "playlist"]
        if mode not in valid_modes:
            return False, f"Invalid repeat mode. Choose from: {', '.join(valid_modes)}"
        
        self.repeat_mode = mode
        return True, f"Repeat mode set to '{mode}'"

    def get_top_songs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top played songs"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT id, title, artist, album, play_count, last_played
                FROM songs
                ORDER BY play_count DESC
                LIMIT ?""",
                (limit,)
            )
            
            top_songs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return top_songs
        except Exception as e:
            print(f"Error getting top songs: {e}")
            return []

    def get_recently_played(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently played songs"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT id, title, artist, album, play_count, last_played
                FROM songs
                WHERE last_played IS NOT NULL
                ORDER BY last_played DESC
                LIMIT ?""",
                (limit,)
            )
            
            recent_songs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return recent_songs
        except Exception as e:
            print(f"Error getting recently played songs: {e}")
            return []

    def rate_song(self, song_id: int, rating: int) -> Tuple[bool, str]:
        """Rate a song (1-5 stars)"""
        if not 1 <= rating <= 5:
            return False, "Rating must be between 1 and 5"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if song exists
            cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (song_id,))
            song_result = cursor.fetchone()
            
            if not song_result:
                conn.close()
                return False, f"Song with ID {song_id} not found"
            
            song_title, song_artist = song_result
            
            # Update song rating
            cursor.execute(
                "UPDATE songs SET rating = ? WHERE id = ?",
                (rating, song_id)
            )
            
            conn.commit()
            conn.close()
            
            return True, f"Rated '{song_title}' by {song_artist} with {rating} stars"
        except Exception as e:
            return False, f"Failed to rate song: {str(e)}"

    def get_song_info(self, song_id: int) -> Dict[str, Any]:
        """Get detailed information about a song"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
            song = cursor.fetchone()
            
            if not song:
                conn.close()
                return {}
            
            song_dict = dict(song)
            
            # Get playlists containing this song
            cursor.execute(
                """SELECT p.name 
                FROM playlists p
                JOIN playlist_songs ps ON p.id = ps.playlist_id
                WHERE ps.song_id = ?""",
                (song_id,)
            )
            
            playlists = [row[0] for row in cursor.fetchall()]
            song_dict["playlists"] = playlists
            
            conn.close()
            return song_dict
        except Exception as e:
            print(f"Error getting song info: {e}")
            return {}

    def get_now_playing(self) -> Dict[str, Any]:
        """Get information about what's currently playing"""
        if not self.current_song:
            return {}
        
        result = {
            "song": self.current_song,
            "is_playing": self.is_playing,
            "volume": self.volume,
            "repeat_mode": self.repeat_mode,
            "shuffle_mode": self.shuffle_mode
        }
        
        if self.current_playlist:
            result["playlist"] = {
                "length": len(self.current_playlist),
                "current_position": -1
            }
            
            # Find position in playlist
            for i, song in enumerate(self.current_playlist):
                if song["id"] == self.current_song["id"]:
                    result["playlist"]["current_position"] = i
                    break
        
        return result

    def delete_playlist(self, playlist_name: str) -> Tuple[bool, str]:
        """Delete a playlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if playlist exists
            cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
            playlist = cursor.fetchone()
            
            if not playlist:
                conn.close()
                return False, f"Playlist '{playlist_name}' not found"
            
            playlist_id = playlist[0]
            
            # Delete playlist (cascade will delete playlist_songs entries)
            cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
            
            conn.commit()
            conn.close()
            
            return True, f"Deleted playlist '{playlist_name}'"
        except Exception as e:
            return False, f"Failed to delete playlist: {str(e)}"

    def remove_song_from_playlist(self, playlist_name: str, song_id: int) -> Tuple[bool, str]:
        """Remove a song from a playlist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get playlist ID
            cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
            playlist_result = cursor.fetchone()
            
            if not playlist_result:
                conn.close()
                return False, f"Playlist '{playlist_name}' not found"
            
            playlist_id = playlist_result[0]
            
            # Check if song exists
            cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (song_id,))
            song_result = cursor.fetchone()
            
            if not song_result:
                conn.close()
                return False, f"Song with ID {song_id} not found"
            
            song_title, song_artist = song_result
            
            # Check if song is in the playlist
            cursor.execute(
                "SELECT id, position FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
                (playlist_id, song_id)
            )
            
            entry = cursor.fetchone()
            if not entry:
                conn.close()
                return False, f"Song '{song_title}' is not in playlist '{playlist_name}'"
            
            entry_id, position = entry
            
            # Remove song from playlist
            cursor.execute(
                "DELETE FROM playlist_songs WHERE id = ?",
                (entry_id,)
            )
            
            # Update positions for remaining songs
            cursor.execute(
                "UPDATE playlist_songs SET position = position - 1 WHERE playlist_id = ? AND position > ?",
                (playlist_id, position)
            )
            
            # Update playlist last_modified timestamp
            cursor.execute(
                "UPDATE playlists SET last_modified = CURRENT_TIMESTAMP WHERE id = ?",
                (playlist_id,)
            )
            
            conn.commit()
            conn.close()
            
            return True, f"Removed '{song_title}' by {song_artist} from playlist '{playlist_name}'"
        except Exception as e:
            return False, f"Failed to remove song from playlist: {str(e)}"

    def import_music_folder(self, folder_path: str) -> Tuple[int, int, List[str]]:
        """
        Import music files from a folder (simulation)
        Returns: (success_count, fail_count, errors)
        """
        if not os.path.isdir(folder_path):
            return 0, 0, [f"Folder not found: {folder_path}"]
        
        # In a real implementation, this would scan the folder for music files,
        # extract metadata, and add them to the database
        
        # Simulate finding some music files
        success_count = 0
        fail_count = 0
        errors = []
        
        # Simulate importing some sample songs
        sample_songs = [
            {"title": "Sample Song 1", "artist": "Artist A", "album": "Album X", "genre": "Rock"},
            {"title": "Sample Song 2", "artist": "Artist B", "album": "Album Y", "genre": "Pop"},
            {"title": "Sample Song 3", "artist": "Artist A", "album": "Album Z", "genre": "Jazz"},
            {"title": "Sample Song 4", "artist": "Artist C", "album": "Album X", "genre": "Classical"},
            {"title": "Sample Song 5", "artist": "Artist B", "album": "Album Z", "genre": "Rock"},
        ]
        
        for song in sample_songs:
            # Simulate a path
            path = os.path.join(folder_path, f"{song['title'].replace(' ', '_')}.mp3")
            
            # Random duration between 2-5 minutes (in seconds)
            duration = random.randint(120, 300)
            
            success, message = self.add_song(
                song["title"], song["artist"], song["album"], song["genre"], path, duration
            )
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(message)
        
        return success_count, fail_count, errors

    def close(self):
        """Close any open resources"""
        # This would close any open audio streams in a real implementation
        self.is_playing = False
        self.current_song = None
        print("Music controller resources released")


# Functions to be called from main.py

def initialize_music_controller():
    """Initialize the music controller and create sample data if needed"""
    controller = MusicController()
    
    # Check if we have any songs
    conn = sqlite3.connect(controller.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM songs")
    song_count = cursor.fetchone()[0]
    conn.close()
    
    if song_count == 0:
        print("Adding sample music to the library...")
        # Add some sample songs
        sample_songs = [
            {"title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera", "genre": "Rock", "duration": 354},
            {"title": "Hotel California", "artist": "Eagles", "album": "Hotel California", "genre": "Rock", "duration": 390},
            {"title": "Imagine", "artist": "John Lennon", "album": "Imagine", "genre": "Pop", "duration": 183},
            {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "album": "Appetite for Destruction", "genre": "Rock", "duration": 356},
            {"title": "Billie Jean", "artist": "Michael Jackson", "album": "Thriller", "genre": "Pop", "duration": 294},
            {"title": "Stairway to Heaven", "artist": "Led Zeppelin", "album": "Led Zeppelin IV", "genre": "Rock", "duration": 482},
            {"title": "Smells Like Teen Spirit", "artist": "Nirvana", "album": "Nevermind", "genre": "Rock", "duration": 301},
            {"title": "Yesterday", "artist": "The Beatles", "album": "Help!", "genre": "Pop", "duration": 125},
            {"title": "Like a Rolling Stone", "artist": "Bob Dylan", "album": "Highway 61 Revisited", "genre": "Rock", "duration": 370},
            {"title": "I Want to Hold Your Hand", "artist": "The Beatles", "album": "Meet the Beatles!", "genre": "Rock", "duration": 146}
        ]
        
        for song in sample_songs:
            controller.add_song(
                song["title"], song["artist"], song["album"], song["genre"], 
                f"sample/{song['title'].replace(' ', '_')}.mp3", song["duration"]
            )
        
        # Create some sample playlists
        controller.create_playlist("Rock Classics")
        controller.create_playlist("Chill Mix")
        controller.create_playlist("All-time Favorites")
        
        # Add songs to playlists
        controller.add_song_to_playlist("Rock Classics", 1)  # Bohemian Rhapsody
        controller.add_song_to_playlist("Rock Classics", 2)  # Hotel California
        controller.add_song_to_playlist("Rock Classics", 4)  # Sweet Child O' Mine
        controller.add_song_to_playlist("Rock Classics", 6)  # Stairway to Heaven
        
        controller.add_song_to_playlist("Chill Mix", 3)  # Imagine
        controller.add_song_to_playlist("Chill Mix", 8)  # Yesterday
        
        controller.add_song_to_playlist("All-time Favorites", 1)  # Bohemian Rhapsody
        controller.add_song_to_playlist("All-time Favorites", 3)  # Imagine
        controller.add_song_to_playlist("All-time Favorites", 5)  # Billie Jean
        controller.add_song_to_playlist("All-time Favorites", 8)  # Yesterday
        
        print("Sample music library created!")
    
    return controller

def manage_music():
    """Main function to manage music playback and library"""
    controller = initialize_music_controller()
    
    while True:
        print("\nMusic Controller")
        print("1. Play a song")
        print("2. Play a playlist")
        print("3. Search music")
        print("4. Create playlist")
        print("5. View playlists")
        print("6. View song details")
        print("7. Import music files")
        print("8. Playback controls")
        print("9. View statistics")
        print("0. Exit")
        
        choice = input("Choose an option (0-9): ")
        
        if choice == "1":
            # Play a song
            search_term = input("Enter song title or artist to search: ")
            results = controller.search_songs(search_term)
            
            if not results:
                print("No songs found matching your search.")
                continue
            
            print("\nSearch Results:")
            for i, song in enumerate(results):
                print(f"{i+1}. {song['title']} by {song['artist']} ({song['album']})")
            
            song_choice = input("\nEnter number to play (or 0 to cancel): ")
            if song_choice == "0" or not song_choice.isdigit():
                continue
                
            song_index = int(song_choice) - 1
            if 0 <= song_index < len(results):
                success, message = controller.play_song(results[song_index]["id"])
                print(message)
            else:
                print("Invalid selection.")
        
        elif choice == "2":
            # Play a playlist
            playlists = controller.list_playlists()
            
            if not playlists:
                print("No playlists found.")
                continue
            
            print("\nAvailable Playlists:")
            for i, playlist in enumerate(playlists):
                print(f"{i+1}. {playlist['name']} ({playlist['song_count']} songs)")
            
            playlist_choice = input("\nEnter number to play (or 0 to cancel): ")
            if playlist_choice == "0" or not playlist_choice.isdigit():
                continue
                
            playlist_index = int(playlist_choice) - 1
            if 0 <= playlist_index < len(playlists):
                shuffle = input("Enable shuffle mode? (y/n): ").lower() == 'y'
                success, message = controller.play_playlist(playlists[playlist_index]["name"], shuffle)
                print(message)
            else:
                print("Invalid selection.")
        
        elif choice == "3":
            # Search music
            search_term = input("Enter search term: ")
            results = controller.search_songs(search_term, limit=20)
            
            if not results:
                print("No songs found matching your search.")
                continue
            
            print("\nSearch Results:")
            for i, song in enumerate(results):
                print(f"{i+1}. {song['title']} by {song['artist']} ({song['album']})")
            
            actions = input("\nActions: (p)lay a song, (a)dd to playlist, or (q)uit: ").lower()
            
            if actions == 'p':
                song_choice = input("Enter song number to play: ")
                if song_choice.isdigit():
                    song_index = int(song_choice) - 1
                    if 0 <= song_index < len(results):
                        success, message = controller.play_song(results[song_index]["id"])
                        print(message)
                    else:
                        print("Invalid selection.")
            
            elif actions == 'a':
                song_choice = input("Enter song number to add: ")
                if song_choice.isdigit():
                    song_index = int(song_choice) - 1
                    if 0 <= song_index < len(results):
                        # List playlists to add to
                        playlists = controller.list_playlists()
                        
                        if not playlists:
                            print("No playlists found. Create one first.")
                            continue
                        
                        print("\nAvailable Playlists:")
                        for i, playlist in enumerate(playlists):
                            print(f"{i+1}. {playlist['name']}")
                        
                        playlist_choice = input("\nEnter playlist number: ")
                        if playlist_choice.isdigit():
                            playlist_index = int(playlist_choice) - 1
                            if 0 <= playlist_index < len(playlists):
                                success, message = controller.add_song_to_playlist(
                                    playlists[playlist_index]["name"], 
                                    results[song_index]["id"]
                                )
                                print(message)
                            else:
                                print("Invalid playlist selection.")
                    else:
                        print("Invalid song selection.")
        
        elif choice == "4":
            # Create playlist
            playlist_name = input("Enter name for new playlist: ")
            if playlist_name:
                success, message = controller.create_playlist(playlist_name)
                print(message)
                
                if success:
                    add_songs = input("Add songs to playlist now? (y/n): ").lower() == 'y'
                    if add_songs:
                        while True:
                            search_term = input("\nEnter song title or artist to search (or 'done' to finish): ")
                            if search_term.lower() == 'done':
                                break
                                
                            results = controller.search_songs(search_term)
                            
                            if not results:
                                print("No songs found matching your search.")
                                continue
                            
                            print("\nSearch Results:")
                            for i, song in enumerate(results):
                                print(f"{i+1}. {song['title']} by {song['artist']} ({song['album']})")
                            
                            song_choice = input("\nEnter number to add (or 0 to cancel): ")
                            if song_choice == "0" or not song_choice.isdigit():
                                continue
                                
                            song_index = int(song_choice) - 1
                            if 0 <= song_index < len(results):
                                success, message = controller.add_song_to_playlist(
                                    playlist_name, 
                                    results[song_index]["id"]
                                )
                                print(message)
                            else:
                                print("Invalid selection.")
        
        elif choice == "5":
            # View playlists
            playlists = controller.list_playlists()
            
            if not playlists:
                print("No playlists found.")
                continue
            
            print("\nYour Playlists:")
            for i, playlist in enumerate(playlists):
                print(f"{i+1}. {playlist['name']} ({playlist['song_count']} songs)")
                print(f"   Created: {playlist['created_date']}")
                print(f"   Last modified: {playlist['last_modified']}")
            
            playlist_choice = input("\nEnter number to view details (or 0 to cancel): ")
            if playlist_choice == "0" or not playlist_choice.isdigit():
                continue
                
            playlist_index = int(playlist_choice) - 1
            if 0 <= playlist_index < len(playlists):
                playlist_name = playlists[playlist_index]["name"]
                songs = controller.get_playlist_songs(playlist_name)
                
                if not songs:
                    print(f"\nPlaylist '{playlist_name}' is empty.")
                    continue
                
                print(f"\nSongs in '{playlist_name}':")
                for i, song in enumerate(songs):
                    print(f"{i+1}. {song['title']} by {song['artist']} ({song['album']})")
                
                actions = input("\nActions: (p)lay playlist, (r)emove song, (d)elete playlist, or (q)uit: ").lower()
                
                if actions == 'p':
                    shuffle = input("Enable shuffle mode? (y/n): ").lower() == 'y'
                    success, message = controller.play_playlist(playlist_name, shuffle)
                    print(message)
                
                elif actions == 'r':
                    song_choice = input("Enter song number to remove: ")
                    if song_choice.isdigit():
                        song_index = int(song_choice) - 1
                        if 0 <= song_index < len(songs):
                            success, message = controller.remove_song_from_playlist(
                                playlist_name, 
                                songs[song_index]["id"]
                            )
                            print(message)
                        else:
                            print("Invalid selection.")
                
                elif actions == 'd':
                    confirm = input(f"Are you sure you want to delete '{playlist_name}'? (y/n): ").lower()
                    if confirm == 'y':
                        success, message = controller.delete_playlist(playlist_name)
                        print(message)
            else:
                print("Invalid selection.")
        
        elif choice == "6":
            # View song details
            search_term = input("Enter song title or artist to search: ")
            results = controller.search_songs(search_term)
            
            if not results:
                print("No songs found matching your search.")
                continue
            
            print("\nSearch Results:")
            for i, song in enumerate(results):
                print(f"{i+1}. {song['title']} by {song['artist']} ({song['album']})")
            
            song_choice = input("\nEnter number to view details (or 0 to cancel): ")
            if song_choice == "0" or not song_choice.isdigit():
                continue
                
            song_index = int(song_choice) - 1
            if 0 <= song_index < len(results):
                song_info = controller.get_song_info(results[song_index]["id"])
                
                if not song_info:
                    print("Song details not found.")
                    continue
                
                print("\nSong Details:")
                print(f"Title: {song_info['title']}")
                print(f"Artist: {song_info['artist']}")
                print(f"Album: {song_info['album'] or 'Unknown'}")
                print(f"Genre: {song_info['genre'] or 'Unknown'}")
                print(f"Duration: {song_info['duration'] // 60}:{song_info['duration'] % 60:02d}")
                print(f"Play Count: {song_info['play_count']}")
                
                if song_info['last_played']:
                    print(f"Last Played: {song_info['last_played']}")
                    
                print(f"Rating: {'★' * song_info['rating']}")
                
                if song_info['playlists']:
                    print(f"In Playlists: {', '.join(song_info['playlists'])}")
                
                actions = input("\nActions: (p)lay song, (r)ate song, or (q)uit: ").lower()
                
                if actions == 'p':
                    success, message = controller.play_song(song_info["id"])
                    print(message)
                
                elif actions == 'r':
                    rating = input("Rate this song (1-5 stars): ")
                    if rating.isdigit() and 1 <= int(rating) <= 5:
                        success, message = controller.rate_song(song_info["id"], int(rating))
                        print(message)
                    else:
                        print("Invalid rating. Please enter a number between 1 and 5.")
            else:
                print("Invalid selection.")
        
        elif choice == "7":
            # Import music files
            folder_path = input("Enter folder path to import: ")
            if folder_path:
                if not os.path.isdir(folder_path):
                    print(f"Folder not found: {folder_path}")
                    continue
                
                print(f"Importing music from {folder_path}...")
                success_count, fail_count, errors = controller.import_music_folder(folder_path)
                
                print(f"Import completed: {success_count} songs imported, {fail_count} failed")
                if errors and input("Show errors? (y/n): ").lower() == 'y':
                    for error in errors:
                        print(f"- {error}")
        
        elif choice == "8":
            # Playback controls
            now_playing = controller.get_now_playing()
            
            if not now_playing:
                print("No song is currently playing.")
                continue
            
            print("\nNow Playing:")
            if now_playing["song"]:
                print(f"{now_playing['song']['title']} by {now_playing['song']['artist']}")
                print(f"Status: {'Playing' if now_playing['is_playing'] else 'Paused'}")
                print(f"Volume: {now_playing['volume']}%")
                print(f"Repeat: {now_playing['repeat_mode']}")
                print(f"Shuffle: {'On' if now_playing['shuffle_mode'] else 'Off'}")
                
                if 'playlist' in now_playing:
                    print(f"Playlist position: {now_playing['playlist']['current_position'] + 1}/{now_playing['playlist']['length']}")
            
            print("\nPlayback Controls:")
            print("1. Play/Pause")
            print("2. Next song")
            print("3. Previous song")
            print("4. Stop")
            print("5. Adjust volume")
            print("6. Toggle shuffle")
            print("7. Change repeat mode")
            
            control_choice = input("\nEnter control number (or 0 to cancel): ")
            
            if control_choice == "1":
                if now_playing['is_playing']:
                    success, message = controller.pause()
                else:
                    success, message = controller.resume()
                print(message)
            
            elif control_choice == "2":
                success, message = controller.next_song()
                print(message)
            
            elif control_choice == "3":
                success, message = controller.previous_song()
                print(message)
            
            elif control_choice == "4":
                success, message = controller.stop()
                print(message)
            
            elif control_choice == "5":
                volume = input(f"Enter volume level (0-100, current: {now_playing['volume']}): ")
                if volume.isdigit():
                    success, message = controller.set_volume(int(volume))
                    print(message)
                else:
                    print("Invalid volume level.")
            
            elif control_choice == "6":
                success, message = controller.toggle_shuffle()
                print(message)
            
            elif control_choice == "7":
                print("\nRepeat Modes:")
                print("1. Off")
                print("2. Repeat song")
                print("3. Repeat playlist")
                
                mode_choice = input("\nEnter mode number: ")
                modes = {"1": "off", "2": "song", "3": "playlist"}
                
                if mode_choice in modes:
                    success, message = controller.set_repeat_mode(modes[mode_choice])
                    print(message)
                else:
                    print("Invalid mode selection.")
        
        elif choice == "9":
            # View statistics
            print("\nMusic Statistics:")
            
            # Show top songs
            top_songs = controller.get_top_songs(5)
            if top_songs:
                print("\nTop Played Songs:")
                for i, song in enumerate(top_songs):
                    print(f"{i+1}. {song['title']} by {song['artist']} - {song['play_count']} plays")
            
            # Show recently played
            recent_songs = controller.get_recently_played(5)
            if recent_songs:
                print("\nRecently Played:")
                for i, song in enumerate(recent_songs):
                    print(f"{i+1}. {song['title']} by {song['artist']} - {song['last_played']}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "0":
            # Exit
            controller.close()
            print("Exiting music controller...")
            break
        
        else:
            print("Invalid option. Please try again.")


def main():
    """Main application function"""
    print("Welcome to the Personal Assistant!")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Task Manager")
        print("2. Note Taking")
        print("3. Calendar/Events")
        print("4. Weather Information")
        print("5. Music Player")
        print("6. Expense Tracker")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == "1":
            # Task Manager functionality
            pass
        
        elif choice == "2":
            # Note Taking functionality
            pass
        
        elif choice == "3":
            # Calendar/Events functionality
            pass
        
        elif choice == "4":
            # Weather Information functionality
            pass
        
        elif choice == "5":
            # Music Player functionality
            manage_music()
        
        elif choice == "6":
            # Expense Tracker functionality
            # Your existing code for expense tracker
            pass
        
        elif choice == "7":
            print("Thank you for using the Personal Assistant!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
