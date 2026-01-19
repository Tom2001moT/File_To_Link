import os
import asyncio
import logging
import aiohttp
import time
from datetime import datetime
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- 1. LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# --- 2. CONFIGURATION ---
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

# --- 3. PYROGRAM CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- 4. HELPER UTILITIES ---

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
    if not media: 
        return "file", 0, "application/octet-stream"
    return (
        getattr(media, "file_name", "file"), 
        getattr(media, "file_size", 0), 
        getattr(media, "mime_type", "application/octet-stream")
    )

# --- 5. BACKGROUND TASKS ---

async def keep_alive():
    if not APP_URL: return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    logger.info(f"Keep-Alive: {resp.status}")
            except: pass
            await asyncio.sleep(600)

async def start_polling():
    logger.info("--- 🚀 STARTING HYBRID POLLER ---")
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

                    if text == "/start":
                        await app.send_message(chat_id, "👋 **Welcome!**\nSend me a file to generate high-speed Stream/Download links.")
                        continue
                    elif text == "/status":
                        await app.send_message(chat_id, f"📊 **Uptime:** `{get_uptime()}`")
                        continue

                    has_media = any(k in msg_data for k in ["document", "video", "audio", "photo"])
                    if not has_media: continue

                    status = await app.send_message(chat_id, "🔄 **Generating Links...**")
                    try:
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, m_id)
                        
                        # Separate links for Download vs Streaming
                        dl_url = f"{APP_URL}/dl/{log_msg.id}"
                        stream_url = f"{APP_URL}/stream/{log_msg.id}"
                        
                        name, size, _ = get_file_info(log_msg)
                        
                        markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("📥 Direct Download", url=dl_url),
                                InlineKeyboardButton("📺 Live Stream", url=stream_url)
                            ]
                        ])

                        success_text = (
                            "✅ **Links Generated!**\n\n"
                            f"📂 **Name:** `{name}`\n"
                            f"⚖️ **Size:** `{humanbytes(size)}`"
                        )
                        
                        await app.edit_message_text(chat_id, status.id, success_text, reply_markup=markup)
                    except Exception as e:
                        logger.error(f"Processing Error: {e}")
                        await app.edit_message_text(chat_id, status.id, f"❌ Error: {e}")

            except Exception as e:
                logger.error(f"Poller Loop Error: {e}")
                await asyncio.sleep(5)

# --- 6. WEB STREAMING SERVER ---

async def handle_request(request):
    """Common handler for both download and streaming requests."""
    try:
        path_type = request.path.split('/')[1] # 'dl' or 'stream'
        message_id = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        
        if not msg or not msg.media: return web.Response(status=404)
        
        name, size, mime = get_file_info(msg)
        
        # KEY LOGIC: 'attachment' forces download, 'inline' tries to play in browser
        disposition = "attachment" if path_type == "dl" else "inline"
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': mime,
            'Content-Disposition': f'{disposition}; filename="{name}"',
            'Content-Length': str(size),
            'Accept-Ranges': 'bytes'
        })
        await response.prepare(request)
        
        async for chunk in app.stream_media(msg): 
            await response.write(chunk)
        return response
    except Exception as e: 
        return web.Response(status=500, text=str(e))

async def health_check(request):
    return web.Response(text=f"Bot is Live!\nUptime: {get_uptime()}")

# --- 7. STARTUP SEQUENCE ---

async def start_services():
    logger.info("--- 🤖 BOT LOGGING IN ---")
    await app.start()
    
    try: await app.get_chat(LOG_CHANNEL)
    except: pass

    server = web.Application()
    # Route both endpoints to the same logic
    server.router.add_get('/dl/{id}', handle_request)
    server.router.add_get('/stream/{id}', handle_request)
    server.router.add_get('/', health_check)
    
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    
    logger.info(f"--- 🌐 WEB SERVER LIVE ON PORT {PORT} ---")
    await asyncio.gather(keep_alive(), start_polling())

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except (KeyboardInterrupt, SystemExit):
        pass
