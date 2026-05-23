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
    in_memory=True,
    workers=20,
    max_concurrent_transmissions=20
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
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0' stop-color='%2300f2fe'/%3E%3Cstop offset='1' stop-color='%23d946ef'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='24' height='24' rx='6' fill='%23030408'/%3E%3Cpath d='M8 6h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2zm2 3v6l5-3-5-3z' fill='url(%23g)'/%3E%3C/svg%3E">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #030408;
            --card-bg: rgba(10, 15, 30, 0.65);
            --border-color: rgba(255, 255, 255, 0.08);
            --primary: #00f2fe;
            --secondary: #4facfe;
            --accent: #d946ef;
            --text-main: #ffffff;
            --text-muted: #94a3b8;
            --glow: 0 0 20px rgba(0, 242, 254, 0.3);
        }}
        
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.06), transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(217, 70, 239, 0.06), transparent 40%),
                linear-gradient(rgba(255, 255, 255, 0.003) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.003) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 20px 20px, 20px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            color: var(--text-main);
            overflow-x: hidden;
            padding: 40px 20px;
            box-sizing: border-box;
        }}

        .glow-sphere {{
            position: absolute;
            width: 250px;
            height: 250px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 242, 254, 0.2) 0%, transparent 70%);
            filter: blur(40px);
            z-index: -1;
            animation: floatGlow 10s infinite alternate ease-in-out;
        }}
        .glow-sphere-1 {{
            top: 15%;
            left: 20%;
        }}
        .glow-sphere-2 {{
            bottom: 15%;
            right: 20%;
            animation-delay: -5s;
        }}

        @keyframes floatGlow {{
            0% {{ transform: translate(0, 0) scale(1); }}
            100% {{ transform: translate(50px, -50px) scale(1.2); }}
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 40px 30px;
            width: 100%;
            max-width: 520px;
            text-align: center;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
            animation: fadeIn 0.6s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 24px;
            padding: 1px;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
            opacity: 0.4;
            transition: opacity 0.3s ease;
        }}
        .card:hover::before {{
            opacity: 0.8;
        }}

        /* LOGO STYLES */
        .logo-container {{
            margin-bottom: 28px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .main-logo {{
            width: 72px;
            height: 72px;
            margin-bottom: 10px;
        }}
        .logo-ring-outer {{
            transform-origin: center;
            animation: cyberSpin 12s linear infinite;
        }}
        @keyframes cyberSpin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .logo-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.3));
        }}
        .logo-subtitle {{
            font-size: 9px;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
            margin-top: 4px;
        }}

        .file-icon-wrapper {{
            position: relative;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 80px;
            height: 80px;
            background: rgba(0, 242, 254, 0.08);
            border: 1px solid rgba(0, 242, 254, 0.2);
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: inset 0 0 15px rgba(0, 242, 254, 0.1);
            animation: pulseGlow 3s infinite ease-in-out;
        }}

        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: inset 0 0 15px rgba(0, 242, 254, 0.1), 0 0 10px rgba(0, 242, 254, 0.05); }}
            50% {{ box-shadow: inset 0 0 25px rgba(0, 242, 254, 0.2), 0 0 20px rgba(0, 242, 254, 0.2); border-color: rgba(0, 242, 254, 0.4); }}
        }}

        .file-icon {{
            font-size: 36px;
            filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.5));
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(0, 242, 254, 0.08);
            border: 1px solid rgba(0, 242, 254, 0.15);
            color: var(--primary);
            padding: 6px 14px;
            border-radius: 50px;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        .status-dot {{
            width: 6px;
            height: 6px;
            background-color: var(--primary);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--primary);
            animation: blink 1.5s infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 0.3; }}
            50% {{ opacity: 1; }}
        }}

        .filename {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 19px;
            font-weight: 700;
            line-height: 1.4;
            color: var(--text-main);
            word-break: break-all;
            margin-bottom: 20px;
            padding: 0 10px;
        }}

        .meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
        }}
        .meta-item {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
        }}
        .meta-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
        .meta-value {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-main);
        }}

        .media-container {{
            margin-bottom: 24px;
            border-radius: 16px;
            overflow: hidden;
            background: #000;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
            position: relative;
        }}
        video, audio {{
            display: block;
            width: 100%;
            outline: none;
        }}
        audio {{
            background: #0d111b;
            padding: 10px;
            box-sizing: border-box;
        }}

        .download-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #030408;
            padding: 16px 28px;
            border-radius: 14px;
            text-decoration: none;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            width: 100%;
            box-sizing: border-box;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
            position: relative;
            overflow: hidden;
        }}
        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(0, 242, 254, 0.5);
            background: linear-gradient(135deg, #00f2fe, #d946ef);
            color: #fff;
        }}
        .download-btn:active {{
            transform: translateY(1px);
        }}
        .download-btn::after {{
            content: '';
            position: absolute;
            top: -50%; left: -60%; width: 20%; height: 200%;
            background: rgba(255, 255, 255, 0.2);
            transform: rotate(30deg);
            transition: all 0.5s ease;
            opacity: 0;
        }}
        .download-btn:hover::after {{
            left: 120%;
            opacity: 1;
        }}

        .stats {{
            margin-top: 20px;
            font-size: 12px;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        .stats svg {{
            width: 14px;
            height: 14px;
            fill: currentColor;
        }}

        /* DEVELOPER BLUEPRINT CARD */
        .dev-section {{
            margin-top: 32px;
            border-top: 1px dashed rgba(0, 242, 254, 0.15);
            padding-top: 24px;
            text-align: left;
        }}
        .dev-title {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 12px;
            opacity: 0.8;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .dev-title::before {{
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--primary);
            box-shadow: 0 0 8px var(--primary);
            border-radius: 50%;
        }}
        .dev-profile-link {{
            text-decoration: none;
            display: block;
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 12px 16px;
            transition: all 0.3s ease;
        }}
        .dev-profile-link:hover {{
            background: rgba(0, 242, 254, 0.03);
            border-color: rgba(0, 242, 254, 0.2);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.05);
            transform: translateY(-1px);
        }}
        .dev-content {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .dev-avatar {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.1);
            background: #111;
            transition: border-color 0.3s ease;
        }}
        .dev-profile-link:hover .dev-avatar {{
            border-color: var(--primary);
        }}
        .dev-info {{
            flex: 1;
            min-width: 0;
        }}
        .dev-name {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 14px;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 2px;
        }}
        .dev-bio {{
            font-size: 11px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }}
        .dev-followers {{
            font-size: 10px;
            color: var(--primary);
            font-weight: 600;
            margin-top: 3px;
        }}
        .dev-arrow {{
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            transition: transform 0.3s ease, color 0.3s ease;
        }}
        .dev-profile-link:hover .dev-arrow {{
            transform: translateX(4px);
            color: var(--primary);
        }}
        .dev-arrow svg {{
            width: 100%;
            height: 100%;
            fill: currentColor;
        }}

        @media (max-width: 480px) {{
            .card {{
                padding: 30px 20px;
                border-radius: 20px;
            }}
            .filename {{
                font-size: 17px;
            }}
            .file-icon-wrapper {{
                width: 70px;
                height: 70px;
                border-radius: 16px;
            }}
            .file-icon {{
                font-size: 30px;
            }}
            .download-btn {{
                padding: 14px 20px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="glow-sphere glow-sphere-1"></div>
    <div class="glow-sphere glow-sphere-2"></div>
    <div class="card">
        <!-- Dynamic Spinning Cyber Logo -->
        <div class="logo-container">
            <svg class="main-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
                <defs>
                    <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#00f2fe" />
                        <stop offset="100%" stop-color="#d946ef" />
                    </linearGradient>
                    <filter id="cyber-glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="6" result="blur" />
                        <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>
                <circle cx="50" cy="50" r="42" fill="none" stroke="url(#logo-grad)" stroke-width="2.5" stroke-dasharray="200 60" class="logo-ring-outer" />
                <circle cx="50" cy="50" r="34" fill="none" stroke="rgba(255, 255, 255, 0.05)" stroke-width="1.5" />
                <g filter="url(#cyber-glow)">
                    <path d="M38 42 A 12 12 0 0 1 62 42" fill="none" stroke="url(#logo-grad)" stroke-width="4.5" stroke-linecap="round" />
                    <path d="M62 58 A 12 12 0 0 1 38 58" fill="none" stroke="url(#logo-grad)" stroke-width="4.5" stroke-linecap="round" />
                    <polygon points="46,45 58,50 46,55" fill="url(#logo-grad)" />
                </g>
            </svg>
            <div class="logo-title">FileToLink</div>
            <div class="logo-subtitle">SECURE CLOUD ENGINE</div>
        </div>

        <div class="status-badge">
            <span class="status-dot"></span>
            Direct Stream Active
        </div>
        
        <div class="file-icon-wrapper">
            <span class="file-icon">{icon}</span>
        </div>
        
        <div class="filename">{filename}</div>
        
        <div class="meta-grid">
            <div class="meta-item">
                <div class="meta-label">File Size</div>
                <div class="meta-value">{size_formatted}</div>
            </div>
            <div class="meta-item">
                <div class="meta-label">Downloads</div>
                <div class="meta-value">{downloads}</div>
            </div>
        </div>

        {media_player}
        
        <a href="/dl/{identifier}" class="download-btn">
            <svg style="width: 18px; height: 18px; fill: currentColor;" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
            Download Now
        </a>
        
        <div class="stats">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
            Permanent high-speed direct link
        </div>

        <!-- Dynamic GitHub Developer Blueprint -->
        <div class="dev-section" id="dev-card">
            <div class="dev-title">Developer Blueprint</div>
            <a href="https://github.com/Tom2001moT" target="_blank" class="dev-profile-link">
                <div class="dev-content">
                    <img id="dev-avatar" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' fill='%23111827'/%3E%3Cpath d='M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.464-1.11-1.464-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0 1 12 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.162 22 16.418 22 12c0-5.523-4.477-10-10-10z' fill='%2394a3b8'/%3E%3C/svg%3E" alt="Avatar" class="dev-avatar">
                    <div class="dev-info">
                        <div class="dev-name" id="dev-name">Analyzing GitHub...</div>
                        <div class="dev-bio" id="dev-bio">Retrieving profile link</div>
                        <div class="dev-followers" id="dev-followers">--</div>
                    </div>
                    <div class="dev-arrow">
                        <svg viewBox="0 0 24 24"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/></svg>
                    </div>
                </div>
            </a>
        </div>
    </div>

    <script>
        async function fetchDevDetails() {{
            try {{
                const res = await fetch('https://api.github.com/users/Tom2001moT');
                if (!res.ok) throw new Error('API Error');
                const data = await res.json();
                document.getElementById('dev-avatar').src = data.avatar_url;
                document.getElementById('dev-name').textContent = data.name || 'Tom';
                document.getElementById('dev-bio').textContent = data.bio || 'Core Developer';
                document.getElementById('dev-followers').textContent = `${{data.followers}} Followers`;
            }} catch (e) {{
                document.getElementById('dev-avatar').src = 'https://avatars.githubusercontent.com/u/10000000?v=4';
                document.getElementById('dev-name').textContent = 'Tom2001moT';
                document.getElementById('dev-bio').textContent = 'System & Bot Developer';
                document.getElementById('dev-followers').textContent = 'GitHub Developer';
            }}
        }}
        window.addEventListener('DOMContentLoaded', fetchDevDetails);
    </script>
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

        lower_filename = filename.lower()
        icon = "📁"
        if mime_type.startswith("video/") or any(ext in lower_filename for ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]):
            icon = "🎥"
        elif mime_type.startswith("audio/") or any(ext in lower_filename for ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]):
            icon = "🎵"
        elif mime_type.startswith("image/"):
            icon = "🖼️"
        elif any(ext in lower_filename for ext in [".zip", ".rar", ".7z", ".tar", ".gz"]):
            icon = "📦"
        elif ".pdf" in lower_filename:
            icon = "📕"

        media_player = ""
        if mime_type.startswith("video/") or any(ext in lower_filename for ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]):
            media_player = f'<div class="media-container"><video controls><source src="/stream/{identifier}" type="{mime_type}">Your browser does not support the video tag.</video></div>'
        elif mime_type.startswith("audio/") or any(ext in lower_filename for ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]):
            media_player = f'<div class="media-container"><audio controls><source src="/stream/{identifier}" type="{mime_type}">Your browser does not support the audio element.</audio></div>'

        html = HTML_TEMPLATE.format(
            filename=filename,
            size_formatted=format_size(file_size),
            identifier=identifier,
            downloads=downloads,
            media_player=media_player,
            icon=icon
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
        
        # Prepare Content-Disposition safely to support Unicode filenames and prevent crashes in aiohttp
        import urllib.parse
        safe_filename = filename.encode('ascii', 'ignore').decode('ascii').strip()
        if not safe_filename:
            safe_filename = "file"
        safe_filename = safe_filename.replace('"', '\\"')
        filename_utf8 = urllib.parse.quote(filename)
        
        disposition = 'inline'
        if is_download:
            disposition = f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{filename_utf8}'
            await database.increment_download(message_id)
            
        if range_header:
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
                    'Content-Disposition': disposition,
                    'X-Accel-Buffering': 'no',
                    'Cache-Control': 'no-cache, no-transform'
                }
            )
            await response.prepare(request)
            if request.method == 'HEAD':
                return response
            
            import math
            chunk_size = 1024 * 1024
            offset_chunks = from_bytes // chunk_size
            limit_chunks = math.ceil((until_bytes + 1) / chunk_size) - offset_chunks
            
            current_byte_offset = offset_chunks * chunk_size
            bytes_to_send = length
            bytes_sent = 0
            
            async for chunk in app.stream_media(msg, offset=offset_chunks, limit=limit_chunks):
                chunk_len = len(chunk)
                chunk_start = current_byte_offset
                chunk_end = current_byte_offset + chunk_len - 1
                
                if chunk_end >= from_bytes and chunk_start <= until_bytes:
                    slice_start = max(0, from_bytes - chunk_start)
                    slice_end = min(chunk_len, until_bytes - chunk_start + 1)
                    
                    sliced_chunk = chunk[slice_start:slice_end]
                    await response.write(sliced_chunk)
                    bytes_sent += len(sliced_chunk)
                    if bytes_sent >= bytes_to_send:
                        break
                        
                current_byte_offset += chunk_len
            return response
        else:
            response = web.StreamResponse(
                status=200,
                headers={
                    'Content-Type': mime_type,
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(file_size),
                    'Content-Disposition': disposition,
                    'X-Accel-Buffering': 'no',
                    'Cache-Control': 'no-cache, no-transform'
                }
            )
            await response.prepare(request)
            if request.method == 'HEAD':
                return response
            async for chunk in app.stream_media(msg, offset=0, limit=0):
                await response.write(chunk)
            return response
    except Exception as e:
        logger.error(f"Error streaming/downloading media: {e}", exc_info=True)
        try:
            return web.Response(status=500, text=str(e))
        except Exception:
            raise e

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
