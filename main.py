#%% [markdown]
# This is the main.py file that I will be using to host most of the main functions of the telegram bot
#%% Import statements
from typing import Final # Import to give the constants a type
from telegram import Update # type: ignore
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes # type: ignore
# -----------
#%% Read the token in the telegram token and define it as TOKEN, and add bot's username
with open('tokens/telegram_token', 'r') as file: token_content = file.read()
TOKEN: Final[str] = token_content.strip()
BOT_USERNAME = '@CodechellaBot'


#%% Commands

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am a songlist compiler. Here's how you can interact with me:\n\n"
        "!add [song_name] - Adds a song to the list. E.g., !add Bohemian Rhapsody\n"
        "!delete [song_name] - Deletes a song from the list if you added it or if you're an admin. E.g., !delete Bohemian Rhapsody\n"
        "!list - Displays all songs in the list with the requester's name.\n\n"
        "Please tell me which songs you want to add to the list, or if you'd like to see the list!")

#%% Songlist handling
songs = {}

async def add_song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Please specify a song to add.')
        return
    song_name = ' '.join(args).strip()
    user = update.effective_user
    if song_name in songs:
        await update.message.reply_text('This song is already on the list.')
    else:
        songs[song_name] = {'user': user.full_name, 'user_id': user.id}
        await update.message.reply_text(f'Added "{song_name}" to the list.')

async def delete_song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text('Please specify a song to delete.')
        return
    song_name = ' '.join(args).strip()
    user = update.effective_user
    if song_name not in songs:
        await update.message.reply_text('This song is not on the list.')
    elif songs[song_name]['user_id'] != user.id:
        await update.message.reply_text('You do not have permission to delete this song.')
    else:
        del songs[song_name]
        await update.message.reply_text(f'Removed "{song_name}" from the list.')

async def list_songs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not songs:
        await update.message.reply_text('The song list is empty.')
        return
    message = "Song list:\n" + '\n'.join([f"{song} - requested by {info['user']}" for song, info in songs.items()])
    await update.message.reply_text(message)



# Saving songlist commands

import json

async def save_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('songs_checkpoint.json', 'w') as f:
        json.dump(songs, f, indent=4, default=str)  # Using default=str to handle any non-serializable types gracefully
    await update.message.reply_text('Checkpoint saved successfully!')

async def load_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('songs_checkpoint.json', 'r') as f:
            global songs
            songs = json.load(f)
        await update.message.reply_text('Checkpoint loaded successfully!')
    except FileNotFoundError:
        await update.message.reply_text('No checkpoint file found.')

#%% Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed: 
        return 'Hey there!'
    
    if 'how are you' in processed:
        return 'I am good!'
    
    if 'charles' in processed:
        return 'I love Charles!'
    
    return 'I do not understand what you wrote...'

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


#%% Logging errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error \n {context.error}')














#%% Final application builder
if __name__ == '__main__':
    print('Starting bot...')
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('help', help_command)) 

    # Saving commands
    app.add_handler(CommandHandler('save', save_checkpoint))
    app.add_handler(CommandHandler('load', load_checkpoint))


    # Handling song commands
    app.add_handler(CommandHandler('add', add_song_command))
    app.add_handler(CommandHandler('delete', delete_song_command))
    app.add_handler(CommandHandler('list', list_songs_command))


    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Check for whether theres a new user message or something we have to respond to: Polling
    # Polls the bot
    print('Polling......')
    app.run_polling(poll_interval = 5, close_loop = False) # Define the interval
    
# %%
