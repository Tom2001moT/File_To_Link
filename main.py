import os
import asyncio
import logging
import aiohttp
import time
import json
import urllib.request
from datetime import datetime
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
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

# Start time for /status command
START_TIME = datetime.now()

# Sanitize Channel ID / Username
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

# --- HELPER FUNCTIONS ---

def get_uptime():
    delta = datetime.now() - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def get_filename(msg_obj):
    # For Pyrogram copy_message results
    if hasattr(msg_obj, 'document') and msg_obj.document:
        return msg_obj.document.file_name or "file.bin"
    if hasattr(msg_obj, 'video') and msg_obj.video:
        return msg_obj.video.file_name or "video.mp4"
    if hasattr(msg_obj, 'audio') and msg_obj.audio:
        return msg_obj.audio.file_name or "audio.mp3"
    return "file"

# --- TASK 1: SELF-PING (STAY AWAKE 24/7) ---
async def keep_alive():
    if not APP_URL:
        print("--- ⚠️ No APP_URL found. Self-ping disabled. ---")
        return

    print(f"--- ⏰ Starting 24/7 Keep-Alive for {APP_URL} ---")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    print(f"--- 💤 Ping Status: {resp.status} at {time.ctime()} ---")
            except Exception as e:
                print(f"--- 💤 Ping Error: {e} ---")
            await asyncio.sleep(600) # 10 minutes

# --- TASK 2: HYBRID POLLING (HANDLES COMMANDS & FILES) ---
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
                    text = msg.get("text", "")

                    # --- COMMAND HANDLERS ---
                    
                    if text.startswith("/start"):
                        welcome_text = (
                            "👋 **Welcome to FileToLink Bot!**\n\n"
                            "I can generate direct download links for any file you send me.\n\n"
                            "🔹 **How to use:** Just send or forward a file here.\n"
                            "🔹 **Commands:** /help, /status, /about\n\n"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        await app.send_message(chat_id, welcome_text)
                        continue

                    if text.startswith("/help"):
                        help_text = (
                            "📖 **Help Menu**\n\n"
                            "1️⃣ **Send a File**: Send any document, video, or audio (up to 2GB).\n"
                            "2️⃣ **Wait**: I will process it and store it in my database.\n"
                            "3️⃣ **Get Link**: You will receive a direct link to download/stream.\n\n"
                            "📌 *Links are permanent as long as the file stays in the log channel.*\n\n"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        await app.send_message(chat_id, help_text)
                        continue

                    if text.startswith("/status"):
                        status_text = (
                            "📊 **System Status**\n\n"
                            f"✅ **Bot:** Online\n"
                            f"⏳ **Uptime:** `{get_uptime()}`\n"
                            f"📡 **Mode:** Hybrid Polling (24/7)\n"
                            f"📂 **Log Channel:** `{LOG_CHANNEL_RAW}`\n"
                            f"🌐 **Server:** Render Cloud \n\n"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        await app.send_message(chat_id, status_text)
                        continue

                    if text.startswith("/about"):
                        await app.send_message(chat_id, "👤 **About**\n\nThis bot was created to provide fast, direct links to Telegram files. Powered by Pyrogram and Render. 🔹 **Developer:** @WhiteDeathGaming **WDG**")
                        continue

                    # --- MEDIA HANDLING ---
                    
                    # Check for media keys (document, video, audio, photo)
                    has_media = any(k in msg for k in ["document", "video", "audio", "photo"])
                    if not has_media:
                        if text and not text.startswith("/"):
                            await app.send_message(chat_id, "❌ **Please send a valid file.**\nUse /help for more info.")
                        continue

                    status = await app.send_message(chat_id, "🔄 **Processing your file...**")
                    try:
                        # Copy message to Log Channel
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, msg_id)
                        
                        file_url = f"{APP_URL}/dl/{log_msg.id}"
                        filename = get_filename(log_msg)
                        
                        success_text = (
                            "✅ **Link Generated!**\n\n"
                            f"📂 **Filename:** `{filename}`\n"
                            f"🔗 **Direct Link:**\n{file_url}\n\n"
                            "⚡ *Direct high-speed download enabled.* \n\n"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        
                        await app.edit_message_text(chat_id, status.id, success_text)
                    except Exception as e:
                        print(f"Processing Error: {e}")
                        await app.edit_message_text(chat_id, status.id, f"❌ **Error:** {e}\n\nPlease check if the bot is an admin in the log channel.")

            except Exception as e:
                print(f"Polling Exception: {e}")
                await asyncio.sleep(5)

# --- TASK 3: STREAMING SERVER ---
async def handle_stream(request):
    try:
        message_id = int(request.match_info['id'])
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
    return web.Response(text=f"Bot is running 24/7\nUptime: {get_uptime()}")

# --- STARTUP ---
async def start_services():
    print("--- 🤖 Starting Telegram Client ---")
    await app.start()
    
    # Resolve channel on startup
    resolved = False
    for i in range(3):
        try:
            print(f"--- 🔎 Attempting to resolve Log Channel: {LOG_CHANNEL} ---")
            chat = await app.get_chat(LOG_CHANNEL)
            print(f"--- ✅ Log Channel Resolved: {chat.title} ---")
            resolved = True
            break
        except Exception as e:
            print(f"--- ⚠️ Resolution attempt {i+1} failed: {e} ---")
            await asyncio.sleep(3)

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
