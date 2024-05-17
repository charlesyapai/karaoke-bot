#%% [markdown]
# This is the main.py file that I will be using to host most of the main functions of the telegram bot
#%% Import statements
import os
import pandas as pd
import numpy as np
from typing import Final # Import to give the constants a type
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup# type: ignore
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler # type: ignore
from match_songs import match_song
from fuzzywuzzy import process



import functools # For logging commands

# -----------
#%% Read the token in the telegram token and define it as TOKEN, and add bot's username
with open('tokens/telegram_token', 'r') as file: token_content = file.read()
TOKEN: Final[str] = token_content.strip()
BOT_USERNAME = '@CodechellaBot'

# for koyeb, import the environment variable
# TOKEN = os.envrion.get("TOKEN")

#%% Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am a songlist compiler! Here's how you can interact with me:\n\n"
        "/add [song_name] - Artist - Adds a song to the list. E.g., /add Bohemian Rhapsody - Queen \n"
        "/delete [song_name] - Deletes a song from the list if you added it or if you're an admin. E.g., /delete Bohemian Rhapsody\n"
        "/list - Displays all songs in the list with the requester's name.\n\n"
        "/listall - Displays all the songs in the list."
        "Please tell me which songs you want to add to the list, or if you'd like to see the list!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am a songlist compiler. Here's how you can interact with me:\n\n"
        "/add [song_name] - Artist - Adds a song to the list. E.g., /add Bohemian Rhapsody - Queen \n"
        "/delete [song_name] - Deletes a song from the list if you added it or if you're an admin. E.g., /delete Bohemian Rhapsody\n"
        "/list - Displays all songs in the list for the specific requester.\n\n"
        "/listall - Displays all the songs in the list."
        "Please tell me which songs you want to add to the list, or if you'd like to see the list!")

#%% Songlist handling

songs_df = pd.DataFrame(columns=[
    'song_name', 'user_full_name', 'user_id', 
    'priority_number', 'matched_song_name', 'genre', 'artist'
])

# Initialize these columns with a default of NaN for now
songs_df['priority_number'] = np.nan
songs_df['matched_song_name'] = pd.NA
songs_df['genre'] = pd.NA
songs_df['artist'] = pd.NA



def log_command(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        command = update.message.text
        print(f"Command: {command} by User: {user.full_name} ({user.id})")  # Logging the command and user info
        await func(update, context)
    return wrapper

@log_command
async def add_song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Please specify a song to add. Format: "/add song name - artist name"')
        return

    # Join arguments and check if there's an artist specified
    input_text = ' '.join(args).strip()
    if '-' in input_text:
        song_name, artist_name = input_text.split('-', 1)
        song_name = song_name.strip()
        artist_name = artist_name.strip()
    else:
        song_name = input_text
        artist_name = None

    # Use match_song to find the best match
    matched_song_name, matched_artist = match_song(song_name, artist_name)
    
    # Query for genres (additional function or API call needed here)
    genre = "Unknown"  # Placeholder until genre functionality is implemented

    user = update.effective_user
    global songs_df
    if matched_song_name in songs_df['song_name'].values:
        await update.message.reply_text(f'This song ({matched_song_name} by {matched_artist}) is already on the list.')
    else:
        new_entry = pd.DataFrame({
            'song_name': [song_name],
            'user_full_name': [user.full_name],
            'user_id': [user.id],
            'matched_song_name': [matched_song_name],
            'artist': [matched_artist],
            'genre': [genre],  # Assuming genre will be added in the future
            'priority_number': [np.nan]
        })
        songs_df = pd.concat([songs_df, new_entry], ignore_index=True)
        await update.message.reply_text(f'Added "{matched_song_name}" by {matched_artist} to the list.')



# @log_command
# async def delete_song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     args = context.args
#     if not args:
#         await update.message.reply_text('Please specify a song to delete.')
#         return
#     song_name = ' '.join(args).strip()
#     user = update.effective_user
#     global songs_df
#     if song_name not in songs_df['song_name'].values:
#         await update.message.reply_text('This song is not on the list.')
#     elif not songs_df[(songs_df['song_name'] == song_name) & (songs_df['user_id'] == user.id)].empty:
#         songs_df = songs_df.drop(songs_df[(songs_df['song_name'] == song_name) & (songs_df['user_id'] == user.id)].index)
#         await update.message.reply_text(f'Removed "{song_name}" from the list.')
#     else:
#         await update.message.reply_text('You do not have permission to delete this song.')

@log_command
async def delete_song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Please specify a song to delete.')
        return

    input_song = ' '.join(args).strip()
    user = update.effective_user
    global songs_df

    # Using fuzzy matching to find the closest song
    choices = songs_df['matched_song_name'].tolist()
    best_match, score = process.extractOne(input_song, choices)

    if score < 75:  # Threshold for match quality
        await update.message.reply_text("No matching song found. Please check your input and try again.")
        return

    # Prepare confirmation buttons
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data=f'delete_yes_{best_match}'),
         InlineKeyboardButton("No", callback_data='delete_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Are you sure you want to delete "{best_match}"?', 
        reply_markup=reply_markup
    )

async def handle_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith('delete_yes_'):
        song_to_delete = data.split('delete_yes_')[1]
        global songs_df

        # Remove all entries of the song regardless of the user who added them
        if song_to_delete in songs_df['song_name'].values:
            songs_df = songs_df[songs_df['song_name'] != song_to_delete]
            await query.edit_message_text(f'Removed "{song_to_delete}" from the list.')
        else:
            await query.edit_message_text("No such song found in the list.")
    elif data == 'delete_no':
        await query.edit_message_text("Deletion cancelled.")






# List songs
@log_command
async def individual_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    global songs_df
    # Convert user ID to string for comparison
    user_id_str = str(user.id)
    # Filter the DataFrame to get only the songs added by the requesting user
    user_songs_df = songs_df[songs_df['user_id'] == user_id_str]

    if user_songs_df.empty:
        await update.message.reply_text('You have not added any songs to the list.')
    else:
        num_songs = len(user_songs_df)
        message = f"Hi 🎶 {user.full_name}! You've added {num_songs} song(s):\n"
        message += "───────────────\n"  # Dotted line for separation
        # Create a numbered list of songs using 'matched_song_name' or 'song_name' if the former is NA
        songs_list = '\n'.join(
            f"{idx + 1}. {row['matched_song_name'] if pd.notna(row['matched_song_name']) else row['song_name']}"
            for idx, row in user_songs_df.iterrows()
        )
        message += songs_list
        await update.message.reply_text(message)



@log_command
async def list_songs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if songs_df.empty:
        await update.message.reply_text('The song list is empty.')
        return

    message = ""
    for name, group in songs_df.groupby('user_full_name'):
        song_list = '\n'.join([
            f"{row['matched_song_name'] if pd.notna(row['matched_song_name']) else row['song_name']} | "
            f"{row['artist'] if pd.notna(row['artist']) else ''} "
            f"{row['priority_number'] if pd.notna(row['priority_number']) else ''}"
            for _, row in group.iterrows()
        ])
        message += f"🎶 {name} 🎶:\n──────────────\n{song_list}\n\n"
    await update.message.reply_text(message)





# Saving songlist commands
@log_command
async def save_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global songs_df
    songs_df.to_csv('songs_checkpoint.csv', index=False)
    await update.message.reply_text('Checkpoint saved successfully!')


async def load_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global songs_df
    try:
        songs_df = pd.read_csv('songs_checkpoint.csv', keep_default_na=False)
        songs_df['priority_number'] = songs_df['priority_number'].apply(pd.to_numeric, errors='coerce')
        songs_df[['matched_song_name', 'genre', 'artist']] = songs_df[['matched_song_name', 'genre', 'artist']].replace({pd.NA: None})
        songs_df['user_id'] = songs_df['user_id'].astype(str)  # Convert user_id to string for consistent data handling
        await update.message.reply_text('Checkpoint loaded successfully!')
    except FileNotFoundError:
        await update.message.reply_text('No checkpoint file found.')




### Advanced Listing Commands
@log_command
async def list_by_singers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global songs_df
    if songs_df.empty:
        await update.message.reply_text('The song list is currently empty.')
        return
    
    message = "🎤 Songs by Singer:\n───────────────\n"
    for artist, group in songs_df.groupby('artist'):
        num_songs = len(group)
        song_list = '\n'.join(f"{idx + 1}. {row['matched_song_name']}" for idx, row in group.iterrows())
        message += f"🎶 {artist if pd.notna(artist) else 'Unknown'} ({num_songs} songs):\n{song_list}\n\n"
    
    await update.message.reply_text(message)

@log_command
async def get_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    global songs_df
    # Convert user ID to string for comparison
    user_id_str = str(user.id)
    # Filter the DataFrame to get only the songs added by the requesting user
    user_songs_df = songs_df[songs_df['user_id'] == user_id_str]

    if user_songs_df.empty:
        await update.message.reply_text("You haven't added any songs to the list yet.")
        return
    
    total_songs = len(user_songs_df)
    songs_by_artist = user_songs_df['artist'].value_counts().to_dict()
    songs_by_genre = user_songs_df['genre'].value_counts().to_dict()

    message = f"🎵 Stats for {user.full_name}:\n"
    message += f"Total songs requested: {total_songs}\n"
    message += "Songs by artist:\n"
    for artist, count in songs_by_artist.items():
        message += f"- {artist if artist else 'Unknown'}: {count}\n"
    message += "Songs by genre:\n"
    for genre, count in songs_by_genre.items():
        message += f"- {genre if genre else 'Unknown'}: {count}\n"

    await update.message.reply_text(message)



#%% Responses
def handle_response(text: str) -> str:
    """
    Processes incoming text messages and returns quirky and personable responses.
    This function makes the bot interact in a fun and engaging manner, responding to greetings,
    checking in on the bot's status, and reacting to mentions of specific names or phrases.
    """
    processed: str = text.lower()

    if 'introduce yourself' in processed:
        return (
            "🎤 **Hello, lovely humans and fellow music enthusiasts! I'm CodechellaBot, your personal karaoke party planner!** 🎉\n\n"
            "As a virtual maestro of melodies, I'm here to help you compile and manage a playlist of your favorite songs to sing along to. "
            "Whether you're gearing up for a night of karaoke or just want to share some tunes, I'm your bot!\n\n"
            "Here’s what I can do for you:\n\n"
            "- Add a Song: Just type `/add [song_name]` to add a new song to our shared playlist. For example, `/add Bohemian Rhapsody`.\n"
            "- Delete a Song: Type `/delete [song_name]` to remove it from the list.\n"
            "- View the Playlist: Type `/list` to see the full list along with who added each song.\n\n"
            "🌟 I'm here to ensure your musical selections are pitch-perfect and everyone gets a chance to shine in the spotlight. So, what are we singing today? 🎶"
        )
    
    # Greeting response with a friendly touch
    if 'hello' in processed:
        return 'Hey there, sunshine! How can I make your day more melodious? 🎶'

    # Responding to inquiries about the bot's status with a positive spin
    if 'how are you' in processed:
        return "I'm just fantastic! Singing my code out loud. And you? 😄"

    # Fun response when a specific name is mentioned
    if 'charles' in processed:
        return "Ah, Charles! He's just awesome 🎷"

    # Adding a humorous touch when the bot does not understand the message
    return "Oops! I tuned out for a moment there. Could you repeat that in the key of C major? 🎹"


#%% Handle how the user can try to contact the bot
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type # This will inform us if it's a group or private chat
    text: str = update.message.text # The incoming processable message
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"') # Get the user ID  and message type

    if message_type == 'group': # Bot to respond only when we call its username
        if BOT_USERNAME in text: 
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text) # Bot will respond to private chats
    
    print('Bot:', response)
    await update.message.reply_text(response)


#%%




#%% Logging errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error \n {context.error}')








#%% Final application builder
if __name__ == '__main__':
    print('Starting bot...')
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', help_command))
    app.add_handler(CommandHandler('help', help_command)) 

    # Saving commands
    app.add_handler(CommandHandler('save', save_checkpoint))
    app.add_handler(CommandHandler('load', load_checkpoint))


    # Handling song commands
    app.add_handler(CommandHandler('add', add_song_command))
    app.add_handler(CommandHandler('delete', delete_song_command))
    app.add_handler(CallbackQueryHandler(handle_delete_confirmation))



    # Listing songs
    app.add_handler(CommandHandler('list', individual_list_command))
    app.add_handler(CommandHandler('listall', list_songs_command))

    # Listing by singers and stats
    app.add_handler(CommandHandler('listbysinger', list_by_singers_command))
    app.add_handler(CommandHandler('getstats', get_stats_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Check for whether theres a new user message or something we have to respond to: Polling
    # Polls the bot
    print('Polling......')
    app.run_polling(poll_interval = 3, close_loop = False) # Define the interval
    
# %%
