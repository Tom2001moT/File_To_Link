import os
import asyncio
import logging
import aiohttp
import time
import re
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

# --- 3. TELEGRAM CLIENT ---
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
    return f"{delta.days}d {delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"

def humanbytes(size):
    if not size: return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0: return f"{size:.2f} {unit}"
        size /= 1024.0

def get_file_info(msg):
    media = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not media: return "file", 0, "video/mp4"
    return (
        getattr(media, "file_name", "video.mp4"), 
        getattr(media, "file_size", 0), 
        getattr(media, "mime_type", "video/mp4")
    )

# --- 5. BACKGROUND TASKS ---

async def keep_alive():
    if not APP_URL: return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    pass
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
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    if msg.get("text") == "/start":
                        await app.send_message(chat_id, "👋 **Send a video to start streaming!**")
                        continue
                    if not any(k in msg for k in ["document", "video", "audio"]): continue
                    
                    status = await app.send_message(chat_id, "🔄 **Processing Video...**")
                    try:
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, msg["message_id"])
                        dl_url = f"{APP_URL}/dl/{log_msg.id}"
                        stream_url = f"{APP_URL}/stream/{log_msg.id}"
                        name, size, _ = get_file_info(log_msg)
                        
                        markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton("📥 Download", url=dl_url),
                             InlineKeyboardButton("📺 Watch Online", url=stream_url)]
                        ])
                        await app.edit_message_text(chat_id, status.id, f"✅ **{name}**\n⚖️ `{humanbytes(size)}`", reply_markup=markup)
                    except Exception as e:
                        await app.edit_message_text(chat_id, status.id, f"❌ Error: {e}")
            except: await asyncio.sleep(5)

# --- 6. WEB SERVER & PLAYER ---

PLAYER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streaming: {filename}</title>
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <style>
        body {{ margin: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; overflow: hidden; }}
        .container {{ width: 100%; max-width: 1000px; padding: 0; position: relative; }}
        .info {{ position: absolute; top: -50px; left: 0; width: 100%; color: #fff; text-align: center; }}
        h2 {{ margin: 5px 0; font-size: 16px; color: #00bfff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .plyr {{ border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="info">
            <h2>{filename}</h2>
        </div>
        <video id="player" playsinline controls data-poster="">
            <source src="{file_url}" type="{mime}" />
        </video>
    </div>
    <script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
    <script>
        const player = new Plyr('#player', {{
            controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'],
            settings: ['captions', 'quality', 'speed', 'loop'],
            tooltips: {{ controls: true, seek: true }},
            speed: {{ selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] }}
        }});
    </script>
</body>
</html>
"""

async def stream_handler(request):
    """Core Streaming Logic supporting Range Requests (Seeking Fix)"""
    mid = int(request.match_info['id'])
    is_dl = request.path.startswith("/dl")
    
    msg = await app.get_messages(LOG_CHANNEL, mid)
    if not msg or not msg.media:
        return web.Response(status=404, text="File Not Found")

    name, size, mime = get_file_info(msg)
    
    range_header = request.headers.get("Range")
    start = 0
    end = size - 1

    if range_header:
        # Match "bytes=start-end"
        match = re.search(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            start = int(match.group(1))
            if match.group(2):
                end = int(match.group(2))
    
    # Calculate chunk size
    chunk_size = (end - start) + 1
    
    headers = {
        'Content-Type': mime,
        'Accept-Ranges': 'bytes',
        'Content-Length': str(chunk_size),
        'Content-Range': f'bytes {start}-{end}/{size}',
    }

    if is_dl:
        headers['Content-Disposition'] = f'attachment; filename="{name}"'
    else:
        headers['Content-Disposition'] = f'inline; filename="{name}"'

    # 206 Partial Content is required for seeking/fast loading
    res = web.StreamResponse(status=206 if range_header else 200, headers=headers)
    await res.prepare(request)
    
    try:
        # We start the stream from the requested offset
        async for chunk in app.stream_media(msg, offset=start):
            if not chunk:
                break
            await res.write(chunk)
            # If we've reached the end of the requested range, stop
            start += len(chunk)
            if start > end:
                break
    except ConnectionResetError:
        pass
    except Exception as e:
        logger.error(f"Stream Error: {e}")
    
    return res

async def handle_player(request):
    """Renders the HTML Player Page"""
    mid = int(request.match_info['id'])
    msg = await app.get_messages(LOG_CHANNEL, mid)
    if not msg: return web.Response(text="File not found")
    name, _, mime = get_file_info(msg)
    file_url = f"{APP_URL}/file/{mid}"
    return web.Response(text=PLAYER_HTML.format(filename=name, file_url=file_url, mime=mime), content_type='text/html')

async def start_services():
    await app.start()
    try: await app.get_chat(LOG_CHANNEL)
    except: pass
    server = web.Application()
    # Updated routes to use the unified high-speed stream_handler
    server.router.add_get('/dl/{id}', stream_handler)
    server.router.add_get('/stream/{id}', handle_player)
    server.router.add_get('/file/{id}', stream_handler)
    server.router.add_get('/', lambda r: web.Response(text="WDG Streamer Active"))
    
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    await asyncio.gather(keep_alive(), start_polling())

if __name__ == "__main__":
    asyncio.run(start_services())
