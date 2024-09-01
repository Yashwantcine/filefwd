from telethon import TelegramClient, events
import pymongo

# Initialize your MongoDB client
mongo_client = pymongo.MongoClient("mongodb+srv://akshat:0BrsgNBlLRWGU1yT@cluster0.u0itcyq.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client['Cluster0']
collection = db['Telegram_files']

# Initialize your Telegram bot client
api_id = '14013342'
api_hash = 'c3e1d740fd207c7ae1b373a7546e8a62'
bot_token = '5307169830:AAGQx5NwBq2gTobDh3rE1N6hKmVY1F9NU78'
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def start_handler(event):
    await event.respond("Welcome! Use /sendfiles to start sending files.")

async def sendfiles_handler(event):
    if event.message.sender_id != (await client.get_me()).id:
        await event.respond("You are not authorized to use this command.")
        return

    files = collection.find({})
    if files.count() == 0:
        await event.respond("No files found in the database.")
        return

    for file in files:
        file_id = file['_id']
        try:
            # Fetch file info from Telegram
            file_info = await client.get_messages(file_id, limit=1)
            if file_info:
                file_message = file_info[0]
                caption = f"📂 File Name: {file['file_name']}\n💾 File Size: {file['file_size']} bytes\n📁 File Type: {file['file_type']}"
                await client.send_file(event.chat_id, file_message.file.id, caption=caption)
            else:
                await event.respond(f"Error retrieving file info for file_id {file_id}")
        except Exception as e:
            await event.respond(f"Error processing file_id {file_id}: {str(e)}")

@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    await start_handler(event)

@client.on(events.NewMessage(pattern='/sendfiles'))
async def handler(event):
    await sendfiles_handler(event)

print("Bot is running...")
client.run_until_disconnected()
