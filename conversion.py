import pandas as pd
import json

# Load JSON data from file
with open('songs_checkpoint.json', 'r') as file:
    songs_dict = json.load(file)

# Convert the dictionary to a DataFrame
songs_df = pd.DataFrame.from_dict(songs_dict, orient='index')
songs_df.index.name = 'song_name'  # Adding an index name if you want to include song names as a column in CSV

# Rename the 'user' column to 'user_full_name'
songs_df.rename(columns={'user': 'user_full_name'}, inplace=True)
# Save the DataFrame to a CSV file
songs_df.to_csv('songs.csv')