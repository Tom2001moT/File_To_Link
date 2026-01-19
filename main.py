import os
import asyncio
import logging
import aiohttp
import time
import json
import urllib.request
from datetime import datetime
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL_RAW = os.environ.get("LOG_CHANNEL", "@wdgfiletolinkbot")
PORT = int(os.environ.get("PORT", 8080))
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

START_TIME = datetime.now()

try:
    if LOG_CHANNEL_RAW.startswith("-") or LOG_CHANNEL_RAW.isdigit():
        LOG_CHANNEL = int(LOG_CHANNEL_RAW)
    else:
        LOG_CHANNEL = LOG_CHANNEL_RAW
except ValueError:
    LOG_CHANNEL = LOG_CHANNEL_RAW 

# --- TELEGRAM CLIENT ---
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
    if hasattr(msg_obj, 'document') and msg_obj.document:
        return msg_obj.document.file_name or "file.bin"
    if hasattr(msg_obj, 'video') and msg_obj.video:
        return msg_obj.video.file_name or "video.mp4"
    if hasattr(msg_obj, 'audio') and msg_obj.audio:
        return msg_obj.audio.file_name or "audio.mp3"
    return "file"

# --- TASK 1: SELF-PING (KEEP-ALIVE) ---
async def keep_alive():
    if not APP_URL:
        return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    pass
            except:
                pass
            await asyncio.sleep(600)

# --- TASK 2: HYBRID POLLING (LISTENERS) ---
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

                    # Commands
                    if text.startswith("/start"):
                        await app.send_message(chat_id, "👋 **Send me a file to generate links!**")
                        continue
                        
                    if text.startswith("/status"):
                        await app.send_message(chat_id, f"📊 **Uptime:** `{get_uptime()}`")
                        continue

                    # Media Handling
                    has_media = any(k in msg for k in ["document", "video", "audio", "photo"])
                    if not has_media: continue

                    # Start processing
                    status = await app.send_message(chat_id, "🔄 **Generating Links...**")
                    
                    try:
                        # Copy to Log Channel
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, msg_id)
                        
                        file_url = f"{APP_URL}/dl/{log_msg.id}"
                        filename = get_filename(log_msg)
                        
                        # --- CONSTRUCT BUTTONS ---
                        # We use the same URL for both buttons, as our server handles both 
                        # downloading and streaming via the same stream response.
                        reply_markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("📥 Direct Download", url=file_url),
                                InlineKeyboardButton("📺 Live Stream", url=file_url)
                            ]
                        ])

                        success_text = (
                            "✅ **File Successfully Processed!**\n\n"
                            f"📂 **Name:** `{filename}`\n\n"
                            f"🔗 **Download Link:**\n`{file_url}`\n\n"
                            "🚀 *Click buttons below for direct actions:* "
                        )
                        
                        await app.edit_message_text(
                            chat_id=chat_id,
                            message_id=status.id,
                            text=success_text,
                            reply_markup=reply_markup,
                            parse_mode=enums.ParseMode.MARKDOWN
                        )
                        
                    except Exception as e:
                        print(f"Error: {e}")
                        await app.edit_message_text(chat_id, status.id, f"❌ Error: {e}")

            except Exception as e:
                print(f"Polling Exception: {e}")
                await asyncio.sleep(5)

# --- TASK 3: STREAMING SERVER ---
async def handle_stream(request):
    try:
        message_id = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        if not msg or not msg.media: return web.Response(status=404)
        
        media = getattr(msg, msg.media.value)
        filename = get_filename(msg)
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(media.file_size),
            'Accept-Ranges': 'bytes' # Needed for streaming players (VLC, etc.)
        })
        await response.prepare(request)
        async for chunk in app.stream_media(msg): 
            await response.write(chunk)
        return response
    except Exception as e: 
        return web.Response(status=500, text=str(e))

async def health_check(request):
    return web.Response(text="Bot is running!")

# --- STARTUP ---
async def start_services():
    print("--- Starting Bot ---")
    await app.start()
    
    try: await app.get_chat(LOG_CHANNEL)
    except: pass

    server = web.Application()
    server.router.add_get('/dl/{id}', handle_stream)
    server.router.add_get('/', health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    
    await asyncio.gather(keep_alive(), start_polling())

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except (KeyboardInterrupt, SystemExit):
        pass

