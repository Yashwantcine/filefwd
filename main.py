from telethon import TelegramClient, events
from telethon.sync import TelegramClient as SyncClient
import pymongo
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# MongoDB connection details
MONGO_URI = "mongodb+srv://akshat:0BrsgNBlLRWGU1yT@cluster0.u0itcyq.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "Cluster0"
COLLECTION_NAME = "Telegram_files"

# Telegram API credentials
API_ID = 14013342
API_HASH = 'c3e1d740fd207c7ae1b373a7546e8a62'
BOT_TOKEN = '5307169830:AAGQx5NwBq2gTobDh3rE1N6hKmVY1F9NU78'
CHANNEL_ID = -1002222995427

# Initialize MongoDB client and collection
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# Initialize Telegram client
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Global variable to control file sending
send_files = False

async def send_file(file_id, file_info):
    try:
        # Retrieve file information
        file = await client.download_media(file_id)
        caption = f"📂 {file_info.get('file_name', 'Unknown')} 🗂️\nSize: {file_info.get('file_size', 'Unknown')} bytes\nType: {file_info.get('file_type', 'Unknown')}\n"
        await client.send_file(CHANNEL_ID, file, caption=caption)
        logging.info(f"Sent file {file_info.get('file_name', 'Unknown')} to channel")
    except Exception as e:
        logging.error(f"Error sending file_id {file_id}: {e}")

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "👋 Welcome! Use the /sendfiles command to start sending files from the database.\n"
        "📝 To view available files, send a message in the format `/file <file_ref>`."
    )

@client.on(events.NewMessage(pattern='/sendfiles'))
async def send_files_command(event):
    global send_files
    if not send_files:
        send_files = True
        await event.respond("✅ File sending initiated.")
        await send_all_files()
    else:
        await event.respond("🔄 File sending is already in progress.")

async def send_all_files():
    global send_files
    try:
        files = collection.find()
        for file_info in files:
            if send_files:
                file_id = file_info.get('file_id')
                await send_file(file_id, file_info)
            else:
                break
    except Exception as e:
        logging.error(f"Error retrieving files: {e}")
    finally:
        send_files = False

@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    global send_files
    send_files = False
    await event.respond("⛔ File sending stopped.")

if __name__ == '__main__':
    print("Starting bot...")
    client.run_until_disconnected()
