import os
import asyncio
import logging
import aiohttp
import time
import io
import qrcode
from datetime import datetime
from pyrogram import Client, filters, idle
from aiohttp import web
import database
from dotenv import load_dotenv

load_dotenv()

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL_RAW = os.environ.get("LOG_CHANNEL", "@wdgfiletolinkbot")
PORT = int(os.environ.get("PORT", 8080))
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8080")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

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
    in_memory=True
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

def get_filesize(msg_obj):
    if hasattr(msg_obj, 'document') and msg_obj.document:
        return msg_obj.document.file_size or 0
    if hasattr(msg_obj, 'video') and msg_obj.video:
        return msg_obj.video.file_size or 0
    if hasattr(msg_obj, 'audio') and msg_obj.audio:
        return msg_obj.audio.file_size or 0
    if hasattr(msg_obj, 'photo') and msg_obj.photo:
        return getattr(msg_obj.photo, 'file_size', 0)
    return 0

def format_size(size_bytes):
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    bio.name = 'qrcode.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# --- TASK 1: SELF-PING (STAY AWAKE 24/7) ---
async def keep_alive():
    if not APP_URL:
        print("--- [WARNING] No APP_URL found. Self-ping disabled. ---")
        return

    print(f"--- [INFO] Starting 24/7 Keep-Alive for {APP_URL} ---")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    print(f"--- [PING] Status: {resp.status} at {time.ctime()} ---")
            except Exception as e:
                print(f"--- [PING ERROR] {e} ---")
            await asyncio.sleep(600) # 10 minutes

# --- BOT HANDLERS ---

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    print("--- [INFO] Received /start ---")
    await database.add_user(message.from_user.id)
    welcome_text = (
        "👋 **Welcome to FileToLink Bot!**\n\n"
        "I can generate direct download links for any file you send me.\n\n"
        "🔹 **How to use:** Just send or forward a file here.\n"
        "🔹 **Commands:** /help, /status, /myfiles, /about\n\n"
        " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
    )
    await message.reply_text(welcome_text)

@app.on_message(filters.command("myfiles") & filters.private)
async def myfiles_cmd(client, message):
    files = await database.get_user_files(message.from_user.id)
    if not files:
        await message.reply_text("📁 **Your Files**\n\nYou haven't uploaded any files yet.")
        return
    
    response_text = "📁 **Your Last 50 Files:**\n\n"
    for f_msg_id, f_name, f_dls in files:
        link = f"{APP_URL}/view/{f_msg_id}"
        response_text += f"📄 `{f_name}`\n🔗 {link}\n📥 Downloads: {f_dls}\n\n"
    
    await message.reply_text(response_text, disable_web_page_preview=True)

@app.on_message(filters.command("users") & filters.private)
async def users_cmd(client, message):
    if message.from_user.id != ADMIN_ID: return
    users = await database.get_all_users()
    await message.reply_text(f"👥 **Total Users:** {len(users)}")

@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(client, message):
    if message.from_user.id != ADMIN_ID: return
    if len(message.command) < 2:
        await message.reply_text("⚠️ Usage: /broadcast [message]")
        return
    b_msg = message.text.split(None, 1)[1]
    users = await database.get_all_users()
    sent = 0
    for uid in users:
        try:
            await client.send_message(uid, f"📢 **Broadcast:**\n\n{b_msg}")
            sent += 1
            await asyncio.sleep(0.1)
        except:
            pass
    await message.reply_text(f"✅ Broadcast sent to {sent}/{len(users)} users.")

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    help_text = (
        "📖 **Help Menu**\n\n"
        "1️⃣ **Send a File**: Send any document, video, or audio (up to 2GB).\n"
        "2️⃣ **Wait**: I will process it and store it in my database.\n"
        "3️⃣ **Get Link**: You will receive a landing page link, download link, and QR Code!\n\n"
        "📌 *Links are permanent as long as the file stays in the log channel.*\n\n"
        " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
    )
    await message.reply_text(help_text)

@app.on_message(filters.command("status") & filters.private)
async def status_cmd(client, message):
    total_dls = await database.get_total_downloads()
    status_text = (
        "📊 **System Status**\n\n"
        f"✅ **Bot:** Online\n"
        f"⏳ **Uptime:** `{get_uptime()}`\n"
        f"📡 **Mode:** Pyrogram Native (24/7)\n"
        f"📂 **Log Channel:** `{LOG_CHANNEL_RAW}`\n"
        f"📥 **Total Downloads Served:** `{total_dls}`\n"
        f"🌐 **Server:** Render Cloud \n\n"
        " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
    )
    await message.reply_text(status_text)

@app.on_message(filters.command("about") & filters.private)
async def about_cmd(client, message):
    await message.reply_text("👤 **About**\n\nThis bot was created to provide fast, direct links to Telegram files. Powered by Pyrogram and Render. 🔹 **Developer:** @WhiteDeathGaming **WDG**")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_media(client, message):
    await database.add_user(message.from_user.id)
    status_msg = await message.reply_text("🔄 **Processing your file...**")
    try:
        # Copy message to Log Channel
        log_msg = await message.copy(LOG_CHANNEL)
        
        view_url = f"{APP_URL}/view/{log_msg.id}"
        dl_url = f"{APP_URL}/dl/{log_msg.id}"
        
        filename = get_filename(message)
        file_size = get_filesize(message)
        
        # Save to database
        await database.add_file(message.from_user.id, log_msg.id, filename, file_size)
        
        # Generate QR Code
        qr_bio = generate_qr(view_url)
        
        success_text = (
            "✅ **Link Generated!**\n\n"
            f"📂 **Filename:** `{filename}`\n"
            f"📦 **Size:** `{format_size(file_size)}`\n\n"
            f"🌐 **Web Preview:**\n{view_url}\n\n"
            f"🔗 **Direct Download:**\n{dl_url}\n\n"
            "⚡ *Scan the QR code to open on mobile!*"
        )
        
        await message.reply_photo(photo=qr_bio, caption=success_text)
        await status_msg.delete()
        
    except Exception as e:
        print(f"Processing Error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {e}\n\nPlease check if the bot is an admin in the log channel.")

@app.on_message(filters.command("short") & filters.private)
async def short_cmd(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ Usage: `/short custom_name`\nMust be replied to a generated link message.")
        return
        
    short_name = message.command[1]
    
    if not message.reply_to_message:
        await message.reply_text("⚠️ You must reply to the bot's message containing the generated link.")
        return
        
    text = message.reply_to_message.caption or message.reply_to_message.text
    if not text:
        return
        
    match = re.search(r"/view/(\d+)", text)
    if not match:
        await message.reply_text("❌ Could not find a valid generated link in that message.")
        return
        
    msg_id = int(match.group(1))
    
    success = await database.set_shortlink(msg_id, short_name)
    if success:
        view_url = f"{APP_URL}/view/{short_name}"
        dl_url = f"{APP_URL}/dl/{short_name}"
        
        await message.reply_text(f"✅ **Shortlink Created!**\n\n🌐 **Web Preview:**\n{view_url}\n\n🔗 **Direct Download:**\n{dl_url}")
    else:
        await message.reply_text("❌ **Shortlink already exists!** Please choose a different name.")

@app.on_message(filters.private & ~filters.command(["start", "myfiles", "users", "broadcast", "help", "status", "about", "short"]))
async def invalid_message(client, message):
    print(f"--- [INFO] Received unhandled text: {message.text} ---")
    await message.reply_text("❌ **Please send a valid file.**\nUse /help for more info.")

import mimetypes
import re

# --- TASK 3: STREAMING SERVER & WEB PAGES ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download {filename} - FileToLink</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #1c1e21;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 400px;
            text-align: center;
        }}
        .icon {{
            font-size: 60px;
            margin-bottom: 20px;
        }}
        .filename {{
            font-size: 20px;
            font-weight: bold;
            word-break: break-all;
            margin-bottom: 10px;
        }}
        .size {{
            color: #65676B;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .download-btn {{
            display: inline-block;
            background-color: #1877f2;
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
            transition: background-color 0.2s;
            width: 100%;
            box-sizing: border-box;
        }}
        .download-btn:hover {{
            background-color: #166fe5;
        }}
        .stats {{
            margin-top: 20px;
            font-size: 12px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">📁</div>
        <div class="filename">{filename}</div>
        <div class="size">Size: {size_formatted}</div>
        
        {media_player}
        
        <a href="/dl/{identifier}" class="download-btn">⬇️ Download Now</a>
        
        <div class="stats">
            Downloaded {downloads} times
        </div>
    </div>
</body>
</html>
"""

async def get_message_id_from_request(request):
    identifier = request.match_info['id']
    file_record = await database.get_file_by_identifier(identifier)
    if file_record:
        return file_record[2], file_record
    elif identifier.isdigit():
        return int(identifier), None
    return None, None

async def handle_view(request):
    try:
        identifier = request.match_info['id']
        message_id, file_record = await get_message_id_from_request(request)
        if not message_id: return web.Response(status=404, text="Not Found")
        
        if file_record:
            filename = file_record[3]
            file_size = file_record[4]
            downloads = file_record[5]
        else:
            msg = await app.get_messages(LOG_CHANNEL, message_id)
            if not msg or not msg.media: return web.Response(status=404, text="Not Found")
            media = getattr(msg, msg.media.value)
            filename = getattr(media, "file_name", "file") or "file"
            file_size = getattr(media, "file_size", 0) or 0
            downloads = 0

        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or 'application/octet-stream'

        media_player = ""
        if mime_type.startswith("video/"):
            media_player = f'<video controls style="width: 100%; border-radius: 8px; margin-bottom: 20px;"><source src="/stream/{identifier}" type="{mime_type}">Your browser does not support the video tag.</video>'
        elif mime_type.startswith("audio/"):
            media_player = f'<audio controls style="width: 100%; margin-bottom: 20px;"><source src="/stream/{identifier}" type="{mime_type}">Your browser does not support the audio element.</audio>'

        html = HTML_TEMPLATE.format(
            filename=filename,
            size_formatted=format_size(file_size),
            identifier=identifier,
            downloads=downloads,
            media_player=media_player
        )
        return web.Response(text=html, content_type='text/html')
        
    except Exception as e:
        return web.Response(status=500, text=str(e))

async def handle_stream(request):
    try:
        message_id, _ = await get_message_id_from_request(request)
        if not message_id: return web.Response(status=404, text="Not Found")
        
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        if not msg or not msg.media: return web.Response(status=404, text="Not Found")
        
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "file") or "file"
        file_size = getattr(media, "file_size", 0) or 0
        mime_type = getattr(media, "mime_type", "application/octet-stream")
        
        is_download = request.path.startswith("/dl/")
        range_header = request.headers.get('Range')
        
        if range_header and not is_download:
            from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
            from_bytes = int(from_bytes) if from_bytes else 0
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
            if until_bytes >= file_size:
                until_bytes = file_size - 1
                
            length = until_bytes - from_bytes + 1
            
            response = web.StreamResponse(
                status=206,
                headers={
                    'Content-Type': mime_type,
                    'Content-Range': f'bytes {from_bytes}-{until_bytes}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(length),
                }
            )
            await response.prepare(request)
            async for chunk in app.stream_media(msg, offset=from_bytes, limit=length):
                await response.write(chunk)
            return response
        else:
            if is_download:
                await database.increment_download(message_id)
                
            response = web.StreamResponse(
                status=200,
                headers={
                    'Content-Type': mime_type,
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(file_size),
                    'Content-Disposition': f'attachment; filename="{filename}"' if is_download else 'inline'
                }
            )
            await response.prepare(request)
            async for chunk in app.stream_media(msg): await response.write(chunk)
            return response
    except Exception as e: return web.Response(status=500, text=str(e))

async def health_check(request):
    return web.Response(text=f"Bot is running 24/7\nUptime: {get_uptime()}")

# --- STARTUP ---
async def start_services():
    print("--- [INFO] Starting Telegram Client ---")
    
    # Initialize DB
    await database.init_db()
    
    await app.start()
    
    # Resolve channel on startup
    resolved = False
    for i in range(3):
        try:
            print(f"--- [INFO] Attempting to resolve Log Channel: {LOG_CHANNEL} ---")
            chat = await app.get_chat(LOG_CHANNEL)
            print(f"--- [SUCCESS] Log Channel Resolved: {chat.title} ---")
            resolved = True
            break
        except Exception as e:
            print(f"--- [WARNING] Resolution attempt {i+1} failed: {e} ---")
            await asyncio.sleep(3)

    server = web.Application()
    server.router.add_get('/dl/{id}', handle_stream)
    server.router.add_get('/stream/{id}', handle_stream)
    server.router.add_get('/view/{id}', handle_view)
    server.router.add_get('/', health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
    
    print(f"--- [INFO] Web Server running on port {PORT} ---")

    await asyncio.gather(
        keep_alive(),
        idle()
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_services())
    except (KeyboardInterrupt, SystemExit):
        pass
