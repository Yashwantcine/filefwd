from telethon import TelegramClient, events
from pymongo import MongoClient
import logging
import asyncio

# MongoDB and Telegram API configuration
MONGO_URI = "mongodb+srv://akshat:0BrsgNBlLRWGU1yT@cluster0.u0itcyq.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "Cluster0"
COLLECTION_NAME = "Telegram_files"
API_ID = 14013342
API_HASH = "c3e1d740fd207c7ae1b373a7546e8a62"
BOT_TOKEN = "5307169830:AAGQx5NwBq2gTobDh3rE1N6hKmVY1F9NU78"
CHANNEL_ID = -1002222995427

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize MongoDB client and database
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Initialize Telegram client
client = TelegramClient('bot', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond(
        "Welcome! Use /sendfiles to start sending files. 📂"
    )

@client.on(events.NewMessage(pattern='/sendfiles'))
async def sendfiles_handler(event):
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message("Fetching files from the database... 📦")

        # Fetch all files from MongoDB
        files = collection.find()
        if files.count() == 0:
            await conv.send_message("No files found in the database. 🗂️")
            return

        for file_doc in files:
            file_id = file_doc.get('file_ref')
            if not file_id:
                logging.warning("File reference not found in document: %s", file_doc)
                continue

            try:
                file = await event.client.download_file(file_id)
                caption = f"📁 {file_doc.get('file_name')} \n📂 {file_doc.get('caption', '')}"

                await event.client.send_file(
                    CHANNEL_ID,
                    file,
                    caption=caption
                )
                logging.info(f"Sent file {file_id} successfully.")
            except Exception as e:
                logging.error(f"Error sending file {file_id}: {e}")

        await conv.send_message("All files have been sent. 🚀")

@client.on(events.NewMessage())
async def handle_other_messages(event):
    # Log any other messages for debugging
    logging.debug(f"Received a message: {event.message.text}")

async def main():
    # Start the Telegram client
    await client.start(bot_token=BOT_TOKEN)
    logging.info("Bot is up and running! 🚀")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
