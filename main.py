import os
import asyncio
import logging
import aiohttp
import time
import json
import urllib.request
from pyrogram import Client
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL_RAW = os.environ.get("LOG_CHANNEL", "@wdgfiletolinkbot")
PORT = int(os.environ.get("PORT", 8080))
# Render provides this URL automatically
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

# Sanitize Channel ID / Username
# If it's a number, convert to int. If it's a username, keep as string.
try:
    if LOG_CHANNEL_RAW.startswith("-") or LOG_CHANNEL_RAW.isdigit():
        LOG_CHANNEL = int(LOG_CHANNEL_RAW)
    else:
        LOG_CHANNEL = LOG_CHANNEL_RAW
except ValueError:
    LOG_CHANNEL = LOG_CHANNEL_RAW 

# --- PYROGRAM CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- TASK 1: SELF-PING (STAY AWAKE 24/7) ---
async def keep_alive():
    if not APP_URL:
        print("--- ⚠️ No APP_URL found. Self-ping disabled. ---")
        return

    print(f"--- ⏰ Starting 24/7 Keep-Alive for {APP_URL} ---")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Ping the health check endpoint
                async with session.get(APP_URL, timeout=10) as resp:
                    print(f"--- 💤 Ping Status: {resp.status} at {time.ctime()} ---")
            except Exception as e:
                print(f"--- 💤 Ping Error: {e} ---")
            await asyncio.sleep(600) # 10 minutes

# --- TASK 2: HYBRID POLLING ---
async def start_polling():
    print("--- 🚀 Starting Hybrid Update Poller ---")
    offset = 0
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(base_url, params={"offset": offset, "timeout": 20}) as resp:
                    data = await resp.json()
                
                if not data.get("ok"):
                    await asyncio.sleep(5)
                    continue
                
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" not in update: continue
                    
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    msg_id = msg["message_id"]

                    if msg.get("text", "").startswith("/start"):
                        await app.send_message(chat_id, "👋 **Bot is Online!**\nSend me any file, video, or photo to generate a link.")
                        continue

                    if not any(k in msg for k in ["document", "video", "audio", "photo"]):
                        continue

                    status = await app.send_message(chat_id, "🔄 **Processing...**")
                    try:
                        # Copy message to Log Channel
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, msg_id)
                        
                        file_url = f"{APP_URL}/dl/{log_msg.id}"
                        
                        filename = "file"
                        if log_msg.document: filename = log_msg.document.file_name
                        elif log_msg.video: filename = log_msg.video.file_name or "video.mp4"
                        elif log_msg.audio: filename = log_msg.audio.file_name or "audio.mp3"
                        
                        await app.edit_message_text(
                            chat_id, status.id, 
                            f"✅ **Link Generated!**\n\n📂 **Name:** `{filename}`\n🔗 **Link:**\n{file_url}"
                        )
                    except Exception as e:
                        print(f"Processing Error: {e}")
                        await app.edit_message_text(chat_id, status.id, f"❌ Error: {e}")

            except Exception as e:
                print(f"Polling Exception: {e}")
                await asyncio.sleep(5)

# --- TASK 3: STREAMING SERVER ---
async def handle_stream(request):
    try:
        message_id = int(request.match_info['id'])
        # Fetch message from the resolved LOG_CHANNEL
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        if not msg or not msg.media: return web.Response(status=404, text="Not Found")
        
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "file") or "file"
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(media.file_size)
        })
        await response.prepare(request)
        async for chunk in app.stream_media(msg): await response.write(chunk)
        return response
    except Exception as e: return web.Response(status=500, text=str(e))

async def health_check(request):
    return web.Response(text="Bot is running 24/7")

# --- STARTUP ---
async def start_services():
    print("--- 🤖 Starting Telegram Client ---")
    await app.start()
    
    # Force resolve channel so Pyrogram doesn't throw PeerID error
    resolved = False
    for i in range(5):
        try:
            print(f"--- 🔎 Attempting to resolve Log Channel: {LOG_CHANNEL} ---")
            chat = await app.get_chat(LOG_CHANNEL)
            print(f"--- ✅ Log Channel Resolved: {chat.title} ---")
            resolved = True
            break
        except Exception as e:
            print(f"--- ⚠️ Resolution attempt {i+1} failed: {e} ---")
            await asyncio.sleep(3)

    if not resolved:
        print("--- 🚨 CRITICAL: Could not resolve channel. Ensure the bot is an ADMIN in the channel. ---")

    server = web.Application()
    server.router.add_get('/dl/{id}', handle_stream)
    server.router.add_get('/', health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    
    print(f"--- 🌐 Web Server running on port {PORT} ---")

    await asyncio.gather(
        keep_alive(),
        start_polling()
    )

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except (KeyboardInterrupt, SystemExit):
        pass
