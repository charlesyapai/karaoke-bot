
import musicbrainzngs as mb
import pandas as pd
import time

mb.set_useragent("YourAppName", "0.1", "YourContactInfo")  # always replace "YourAppName" and "YourContactInfo" with your actual app name and contact info.

def fetch_song_versions_batch(songs, artists=None):
    all_data = pd.DataFrame()

    artists = artists if artists is not None else [None] * len(songs)

    for song, artist in zip(songs, artists):
        query = song
        if artist:
            query += f" AND artist:{artist}"

        try:
            result = mb.search_recordings(query=query, limit=25)
            recordings = result.get('recording-list', [])

            data = []
            for recording in recordings:
                artist_name = recording['artist-credit'][0]['artist']['name'] if 'artist-credit' in recording else 'Unknown artist'
                title = recording.get('title', 'Unknown title')
                release_count = len(recording.get('release-list', []))
                score = recording.get('score', 0)
                genre = "Unknown"  # Default if no genre info is available
                release_info = "Unknown"  # Default if no release info is available

                # If release information is available, fetch the first release details
                if recording.get('release-list'):
                    first_release = recording['release-list'][0]
                    release_info = f"{first_release.get('title', 'Unknown')} ({first_release.get('date', 'Unknown')})"

                # Attempt to fetch genre from the work details if linked
                if 'work-relation-list' in recording:
                    for work in recording['work-relation-list']:
                        work_id = work['work']['id']
                        work_details = mb.get_work_by_id(work_id, includes=["tags"])
                        if 'tag-list' in work_details['work']:
                            genre_tags = [tag['name'] for tag in work_details['work']['tag-list']]
                            genre = ', '.join(genre_tags) if genre_tags else "Unknown"
                            break  # Only use the first work's genre information

                data.append({
                    'Title': title,
                    'Artist': artist_name,
                    'Release Count': release_count,
                    'Score': score,
                    'Genre': genre,
                    'Release': release_info
                })

            df = pd.DataFrame(data)
            all_data = pd.concat([all_data, df], ignore_index=True)

        except mb.MusicBrainzError as e:
            print(f"Error with MusicBrainz API for {song}: {e}")

        print(f"Fetched {len(recordings)} records for '{song}' by '{artist}'.")
        time.sleep(1)  # Respect the API's rate limit

    return all_data

# Example usage with a batch of songs
songs = ["Shape of You", "Yellow", "Believer"]

df = fetch_song_versions_batch(songs)
print(df.head(30))
