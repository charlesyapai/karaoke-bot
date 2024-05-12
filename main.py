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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Thanks for chatting with me! I am CodechellaBot!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a songlist compiler. Please tell me which songs you want to add to the list, or if you\'d like to see the list!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command!')



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
    app.add_handler(CommandHandler('start', start_command)) # Define commands
    app.add_handler(CommandHandler('help', help_command)) 
    app.add_handler(CommandHandler('custom', custom_command))   

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Check for whether theres a new user message or something we have to respond to: Polling
    # Polls the bot
    print('Polling......')
    app.run_polling(poll_interval = 5, close_loop = False) # Define the interval
    
# %%
