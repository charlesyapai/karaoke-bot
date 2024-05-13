import pandas as pd
import musicbrainzngs as mb

# Configure the client with your app information
mb.set_useragent("YourAppName", "0.1", "YourContactInfo")

def match_song(song_name, artist_name=None):
    query = song_name
    if artist_name:
        query += f" AND artist:{artist_name}"
    try:
        result = mb.search_recordings(query=query, limit=1)
        recordings = result.get('recording-list', [])
        if recordings:
            recording = recordings[0]
            artist = recording['artist-credit'][0]['artist']['name'] if 'artist-credit' in recording else 'Unknown artist'
            title = recording['title']
            return title, artist
    except mb.MusicBrainzError as e:
        print(f"Error with MusicBrainz API: {e}")
        return song_name, 'Unknown artist'

# Example: Match a song
song_name = "Shape of You"
artist_name = "Ed Sheeran"
matched_song_name, artist = match_song(song_name, artist_name)
print(f"Matched Song: {matched_song_name}, Artist: {artist}")
