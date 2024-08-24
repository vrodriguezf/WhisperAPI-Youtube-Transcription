import os
import sys
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from videoproc import youtube_preprocess
from chunking import chunk_by_size

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY environment variable not found.")
    sys.exit(1)

# Define the start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a YouTube link to transcribe.')

# Define the message handler for YouTube links
def transcribe(update: Update, context: CallbackContext) -> None:
    youtube_link = update.message.text

    try:
        audio_file = youtube_preprocess(youtube_link)
        no_of_chunks = chunk_by_size(audio_file)

        transcript = ""
        for i in range(no_of_chunks):
            curr_file = open(f"process_chunks/chunk{i}.wav", "rb")
            result = openai.Audio.translate("whisper-1", curr_file)
            transcript += result["text"]

        update.message.reply_text(transcript)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

def main() -> None:
    # Set up the Updater with your bot token
    updater = Updater(os.getenv("TELEGRAM_BOT_TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Register the message handler for YouTube links
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, transcribe))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()