import os
import asyncio
import urllib.request
import json
import logging
from pyrogram import Client, filters
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyrogram")
logger.setLevel(logging.INFO)

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
PORT = int(os.environ.get("PORT", 8080))

# --- WEBHOOK CLEAR ---
def nuke_webhook():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True"
        with urllib.request.urlopen(url) as response:
            print(f"--- Webhook Reset: {json.load(response)} ---")
    except Exception as e:
        print(f"--- Webhook Reset Failed: {e} ---")

# --- CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- CATCH-ALL HANDLER (NO FILTERS) ---
@app.on_message()
async def catch_all(client, message):
    print(f"DEBUG: Message Received! ID: {message.id} | Type: {message.media}")
    
    # 1. Reply to /start
    if message.text and message.text.startswith("/start"):
        await message.reply_text("👋 Bot is Online! Send me any file.")
        return

    # 2. Check for Media
    if not message.media:
        await message.reply_text("❌ Please send a File, Video, or Photo.")
        return

    # 3. Process File
    status_msg = await message.reply_text("🔄 **Processing...**", quote=True)
    try:
        log_msg = await message.copy(chat_id=LOG_CHANNEL)
        file_id = log_msg.id
        
        base_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
        stream_link = f"{base_url}/dl/{file_id}"
        
        await status_msg.edit_text(
            f"✅ **File Saved!**\n\n"
            f"📂 **Name:** `{get_filename(log_msg)}`\n"
            f"🔗 **Download Link:**\n{stream_link}"
        )
    except Exception as e:
        print(f"ERROR: {e}")
        await status_msg.edit_text(f"❌ **Error:** {e}")

def get_filename(msg):
    if msg.document: return msg.document.file_name or "file.bin"
    if msg.video: return msg.video.file_name or "video.mp4"
    if msg.audio: return msg.audio.file_name or "audio.mp3"
    if msg.photo: return "photo.jpg"
    return "unknown_file"

# --- WEB SERVER ---
async def handle_stream(request):
    try:
        msg = await app.get_messages(LOG_CHANNEL, int(request.match_info['id']))
        if not msg or not msg.media: return web.Response(status=404, text="Not Found")
        
        media = getattr(msg, msg.media.value)
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{get_filename(msg)}"',
            'Content-Length': str(media.file_size)
        })
        await response.prepare(request)
        async for chunk in app.stream_media(msg): await response.write(chunk)
        return response
    except Exception as e: return web.Response(status=500, text=str(e))

# --- START ---
async def start_services():
    nuke_webhook()
    print("--- Starting Bot ---")
    await app.start()
    print(f"--- Bot Logged In as @{(await app.get_me()).username} ---")
    
    server = web.Application()
    server.router.add_get('/dl/{id}', handle_stream)
    server.router.add_get('/', lambda r: web.Response(text="Bot Running"))
    
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"--- Web Server running on port {PORT} ---")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_services())
