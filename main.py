import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.WARNING) # Reduce noise
logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
PORT = int(os.environ.get("PORT", 8080))

# --- CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- WEB SERVER HANDLERS ---
async def handle_stream(request):
    try:
        message_id = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        if not msg or not msg.media: return web.Response(status=404, text="File Not Found")
        
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "unknown") or "file"
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(media.file_size)
        })
        await response.prepare(request)
        async for chunk in app.stream_media(msg): await response.write(chunk)
        return response
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")

async def health_check(request):
    return web.Response(text="Bot is running")

# --- MANUAL UPDATE FETCHER ---
# This function manually checks for updates if PUSH fails
async def force_fetch_updates():
    print("--- 🚀 Starting Manual Update Fetcher ---")
    offset = 0
    while True:
        try:
            # Manually ask Telegram for updates
            updates = await app.get_updates(offset=offset, limit=100, timeout=10)
            
            for update in updates:
                offset = update.update_id + 1
                
                # We only care about new messages
                if not update.message: continue
                message = update.message
                
                print(f"DEBUG: Manually fetched message {message.id} from {message.chat.id}")
                
                # --- PROCESS MESSAGE ---
                if message.text and message.text.startswith("/start"):
                    await message.reply_text("👋 **Bot is Online (Force Mode)!**\nSend me a file.")
                    continue
                
                if not message.media:
                    await message.reply_text("❌ Please send a file/video/photo.")
                    continue

                # Process File
                status = await message.reply_text("🔄 **Processing...**", quote=True)
                try:
                    log_msg = await message.copy(chat_id=LOG_CHANNEL)
                    link = f"{os.environ.get('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')}/dl/{log_msg.id}"
                    await status.edit_text(f"✅ **Link Generated:**\n{link}")
                except Exception as e:
                    await status.edit_text(f"❌ Error: {e}")
                    
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Fetcher Error: {e}")
            await asyncio.sleep(5)

# --- MAIN STARTUP ---
async def start_services():
    print("--- Starting Bot ---")
    await app.start()
    print(f"--- Bot Logged In as @{(await app.get_me()).username} ---")

    # Start the Web Server
    server = web.Application()
    server.router.add_get('/', health_check)
    server.router.add_get('/dl/{id}', handle_stream)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"--- Web Server running on port {PORT} ---")

    # Start the Manual Fetcher loop
    await force_fetch_updates()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
