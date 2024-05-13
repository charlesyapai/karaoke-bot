import pandas as pd
import json
import numpy as np  # Import numpy to handle NaN

# Load JSON data from file
with open('songs_checkpoint.json', 'r') as file:
    songs_dict = json.load(file)

# Convert the dictionary to a DataFrame
songs_df = pd.DataFrame.from_dict(songs_dict, orient='index')
songs_df.index.name = 'song_name'  # Adding an index name if you want to include song names as a column in CSV

# Rename the 'user' column to 'user_full_name'
songs_df.rename(columns={'user': 'user_full_name'}, inplace=True)

# Initialize new columns with NaN or None
songs_df['priority_number'] = np.nan  # Assuming priority number is a numeric field
songs_df['matched_song_name'] = pd.NA  # For string fields, using pandas NA
songs_df['genre'] = pd.NA
songs_df['artist'] = pd.NA

# Save the DataFrame to a CSV file
songs_df.to_csv('songs.csv')
