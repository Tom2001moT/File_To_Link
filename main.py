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
    logger.info("--- 🚀 STARTING MANUAL HYBRID POLLER ---")
    offset = 0
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(api_url, params={"offset": offset, "timeout": 20}) as resp:
                    data = await resp.json()
                
                if not data or not data.get("ok"):
                    await asyncio.sleep(5)
                    continue
                
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" not in update: continue
                    
                    msg_data = update["message"]
                    chat_id = msg_data["chat"]["id"]
                    msg_id = msg_data["message_id"]
                    text = msg_data.get("text", "").lower().strip()

                    # Handle Commands
                    if text.startswith("/start"):
                        await app.send_message(chat_id, "👋 **Bot Online!**\nSend me any video to generate high-speed links. **WDG**")
                        continue
                    elif text.startswith("/status"):
                        await app.send_message(chat_id, f"📊 **Uptime:** `{get_uptime()}` **WDG**")
                        continue
                    elif text.startswith("/help"):
                        await app.send_message(chat_id, "📖 Send a video -> Wait -> Get Direct Link. **WDG**")
                        continue

                    # Handle Media
                    has_media = any(k in msg_data for k in ["document", "video", "audio", "photo"])
                    if not has_media: continue

                    status = await app.send_message(chat_id, "🔄 **Processing...**")
                    try:
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, msg_id)
                        
                        dl_url = f"{APP_URL}/dl/{log_msg.id}"
                        stream_url = f"{APP_URL}/stream/{log_msg.id}"
                        name, size, _ = get_file_info(log_msg)
                        
                        markup = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("📥 Download", url=dl_url),
                                InlineKeyboardButton("📺 Watch Online", url=stream_url)
                            ]
                        ])

                        await app.edit_message_text(
                            chat_id, status.id,
                            f"✅ **{name}**\n⚖️ `{humanbytes(size)}`",
                            reply_markup=markup
                        )
                    except Exception as e:
                        await app.edit_message_text(chat_id, status.id, f"❌ Error: {e}")

            except Exception as e:
                logger.error(f"Poller Loop Error: {e}")
                await asyncio.sleep(5)

# --- 6. WEB SERVER & INSTANT PLAYER ---

PLAYER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream: {filename}</title>
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <style>
        body {{ margin: 0; background: #000; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        .player-container {{ width: 100%; max-width: 960px; border-radius: 12px; overflow: hidden; background: #111; box-shadow: 0 20px 50px rgba(0,0,0,0.8); }}
        .header {{ padding: 15px; text-align: center; color: #fff; }}
        h1 {{ margin: 0; font-size: 16px; font-weight: 500; color: #00d2ff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .plyr--video {{ height: auto; max-height: 80vh; }}
    </style>
</head>
<body>
    <div class="header"><h1>{filename}</h1></div>
    <div class="player-container">
        <video id="player" playsinline controls preload="metadata">
            <source src="{file_url}" type="{mime}" />
        </video>
    </div>
    <script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const player = new Plyr('#player', {{
                controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'captions', 'settings', 'pip', 'fullscreen'],
                settings: ['captions', 'quality', 'speed', 'loop'],
                speed: {{ selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] }},
                tooltips: {{ controls: true, seek: true }},
                keyboard: {{ focused: true, global: true }}
            }});
            window.player = player;
        }});
    </script>
</body>
</html>
"""

async def stream_handler(request):
    """Instant Streaming Handler with Robust Range Support"""
    try:
        mid = int(request.match_info['id'])
        is_dl = request.path.startswith("/dl")
        msg = await app.get_messages(LOG_CHANNEL, mid)
        if not msg or not msg.media:
            return web.Response(status=404, text="Media not found")

        name, size, mime = get_file_info(msg)
        range_header = request.headers.get("Range")
        
        # Default start/end
        start = 0
        end = size - 1

        # Parse Range Header
        if range_header:
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                start = int(match.group(1))
                if match.group(2):
                    end = int(match.group(2))
        
        # Validate range
        if start >= size:
            return web.Response(status=416, headers={'Content-Range': f'bytes */{size}'})
        
        chunk_length = (end - start) + 1
        
        headers = {
            'Content-Type': mime,
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_length),
            'Content-Range': f'bytes {start}-{end}/{size}',
            'Content-Disposition': f'{"attachment" if is_dl else "inline"}; filename="{name}"',
            'Cache-Control': 'no-cache'
        }

        # 206 Partial Content is critical for modern browsers
        response = web.StreamResponse(status=206 if range_header else 200, headers=headers)
        await response.prepare(request)
        
        try:
            # Stream from Telegram with specific offset
            async for chunk in app.stream_media(msg, offset=start):
                if not chunk: break
                await response.write(chunk)
                start += len(chunk)
                if start > end: break
        except (ConnectionResetError, asyncio.CancelledError):
            pass 
        return response
    except Exception as e:
        logger.error(f"Streaming Error: {e}")
        return web.Response(status=500)

async def handle_player(request):
    """Renders the HTML Player with direct file source"""
    try:
        mid = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, mid)
        if not msg: return web.Response(status=404)
        name, _, mime = get_file_info(msg)
        # We point the <source> to the /file/ endpoint which handles raw range requests
        file_url = f"{APP_URL}/file/{mid}"
        return web.Response(text=PLAYER_HTML.format(filename=name, file_url=file_url, mime=mime), content_type='text/html')
    except: return web.Response(status=404)

# --- 7. STARTUP ---

async def start_services():
    logger.info("--- 🤖 BOT LOGGING IN ---")
    await app.start()
    
    # Warm up channel cache
    try: await app.get_chat(LOG_CHANNEL)
    except: pass

    server = web.Application()
    server.router.add_get('/dl/{id}', stream_handler)
    server.router.add_get('/stream/{id}', handle_player)
    server.router.add_get('/file/{id}', stream_handler)
    server.router.add_get('/', lambda r: web.Response(text=f"Bot Online. Uptime: {get_uptime()}"))
    
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
