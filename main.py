import os
import asyncio
import logging
import aiohttp
import time
import json
from datetime import datetime
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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

START_TIME = datetime.now()

try:
    if str(LOG_CHANNEL_RAW).startswith("-") or str(LOG_CHANNEL_RAW).isdigit():
        LOG_CHANNEL = int(LOG_CHANNEL_RAW)
    else:
        LOG_CHANNEL = LOG_CHANNEL_RAW
except ValueError:
    LOG_CHANNEL = LOG_CHANNEL_RAW 

# --- CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- HELPERS ---
def get_uptime():
    delta = datetime.now() - START_TIME
    days, seconds = delta.days, delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

def humanbytes(size):
    if not size: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0: return f"{size:.2f} {unit}"
        size /= 1024.0

def get_file_info(msg):
    media = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not media: return "file", 0, "application/octet-stream"
    return getattr(media, "file_name", "file"), getattr(media, "file_size", 0), getattr(media, "mime_type", "application/octet-stream")

# --- BACKGROUND TASKS ---
async def keep_alive():
    """Prevents Render sleep mode"""
    if not APP_URL: return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    logger.info(f"Self-Ping Status: {resp.status}")
            except: pass
            await asyncio.sleep(600)

async def start_polling():
    """Force-fetch updates directly from Telegram API"""
    logger.info("--- 🚀 STARTING MANUAL HTTP POLLER ---")
    offset = 0
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(api_url, params={"offset": offset, "timeout": 20}) as resp:
                    data = await resp.json()
                
                if not data.get("ok"):
                    await asyncio.sleep(5)
                    continue
                
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" not in update: continue
                    
                    msg_data = update["message"]
                    chat_id = msg_data["chat"]["id"]
                    m_id = msg_data["message_id"]
                    text = msg_data.get("text", "")

                    # 1. Handle Commands
                    if text == "/start":
                        await app.send_message(chat_id, "👋 **Bot is Online!**\nSend me a file to get links.")
                        continue
                    elif text == "/help":
                        await app.send_message(chat_id, "📖 **Help:** Just send a file (up to 2GB) and I'll generate links.")
                        continue
                    elif text == "/status":
                        await app.send_message(chat_id, f"📊 **Uptime:** `{get_uptime()}`\n📡 **Mode:** Active Polling")
                        continue

                    # 2. Handle Files
                    has_media = any(k in msg_data for k in ["document", "video", "audio", "photo"])
                    if not has_media: continue

                    status = await app.send_message(chat_id, "🔄 **Processing...**")
                    try:
                        # Copy to Log Channel
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, m_id)
                        
                        f_url = f"{APP_URL}/dl/{log_msg.id}"
                        name, size, _ = get_file_info(log_msg)
                        
                        markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("📥 Direct Download", url=f_url),
                                InlineKeyboardButton("📺 Live Stream", url=f_url)
                            ]
                        ])

                        await app.edit_message_text(
                            chat_id, status.id,
                            f"✅ **Link Ready!**\n\n📂 **Name:** `{name}`\n⚖️ **Size:** `{humanbytes(size)}`\n\n🔗 `{f_url}`",
                            reply_markup=markup
                        )
                    except Exception as e:
                        logger.error(f"Processing Error: {e}")
                        await app.edit_message_text(chat_id, status.id, f"❌ Error: {e}")

            except Exception as e:
                logger.error(f"Poller Exception: {e}")
                await asyncio.sleep(5)

# --- SERVER ---
async def handle_stream(request):
    try:
        m_id = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, m_id)
        if not msg or not msg.media: return web.Response(status=404)
        
        name, size, mime = get_file_info(msg)
        response = web.StreamResponse(status=200, headers={
            'Content-Type': mime,
            'Content-Disposition': f'attachment; filename="{name}"',
            'Content-Length': str(size),
            'Accept-Ranges': 'bytes'
        })
        await response.prepare(request)
        async for chunk in app.stream_media(msg): await response.write(chunk)
        return response
    except: return web.Response(status=500)

async def start_services():
    logger.info("--- 🤖 BOT LOGGING IN ---")
    await app.start()
    
    # Pre-cache channel
    try: await app.get_chat(LOG_CHANNEL)
    except: pass

    server = web.Application()
    server.router.add_get('/dl/{id}', handle_stream)
    server.router.add_get('/', lambda r: web.Response(text="Bot is Active"))
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    
    logger.info(f"--- 🌐 SERVER LIVE ON PORT {PORT} ---")
    await asyncio.gather(keep_alive(), start_polling())

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except:
        pass
