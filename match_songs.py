import pandas as pd
import musicbrainzngs as mb

# Configure the client with your app information
mb.set_useragent("YourAppName", "0.1", "YourContactInfo")

import musicbrainzngs as mb

def match_song(song_name, artist_name=None):
    query = song_name
    if artist_name:
        query += f" AND artist:{artist_name}"

    try:
        result = mb.search_recordings(query=query, limit=5)  # Search for a few more results
        recordings = result.get('recording-list', [])

        if not recordings:
            return song_name, 'Unknown artist'

        # Example heuristic: Choose the recording with the most releases
        best_recording = max(recordings, key=lambda rec: len(rec.get('release-list', [])))
        artist = best_recording['artist-credit'][0]['artist']['name'] if 'artist-credit' in best_recording else 'Unknown artist'
        title = best_recording['title']

        return title, artist

    except mb.MusicBrainzError as e:
        print(f"Error with MusicBrainz API: {e}")
        return song_name, 'Unknown artist'


# Example: Match a song
song_name = "I See Fire"
artist_name = ""
matched_song_name, artist = match_song(song_name, artist_name)
print(f"Matched Song: {matched_song_name}, Artist: {artist}")
