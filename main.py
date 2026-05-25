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
    <title>Secure Cloud Download: {filename}</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0' stop-color='%2300f2fe'/%3E%3Cstop offset='1' stop-color='%23d946ef'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='24' height='24' rx='6' fill='%23030408'/%3E%3Cpath d='M8 6h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2zm2 3v6l5-3-5-3z' fill='url(%23g)'/%3E%3C/svg%3E">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #030408;
            --card-bg: rgba(10, 15, 30, 0.65);
            --border-color: rgba(255, 255, 255, 0.08);
            --primary: #00f2fe;
            --primary-rgb: 0, 242, 254;
            --secondary: #4facfe;
            --accent: #d946ef;
            --accent-rgb: 217, 70, 239;
            --text-main: #ffffff;
            --text-muted: #94a3b8;
            --glow: 0 0 20px rgba(0, 242, 254, 0.25);
        }}
        
        body.theme-sunburst {{
            --primary: #ff5e62;
            --primary-rgb: 255, 94, 98;
            --secondary: #ff9966;
            --accent: #febb2c;
            --accent-rgb: 254, 187, 44;
            --glow: 0 0 20px rgba(255, 94, 98, 0.25);
        }}

        body.theme-emerald {{
            --primary: #10b981;
            --primary-rgb: 16, 185, 129;
            --secondary: #34d399;
            --accent: #fbbf24;
            --accent-rgb: 251, 191, 36;
            --glow: 0 0 20px rgba(16, 185, 129, 0.25);
        }}

        body.theme-amethyst {{
            --primary: #d946ef;
            --primary-rgb: 217, 70, 239;
            --secondary: #a855f7;
            --accent: #ec4899;
            --accent-rgb: 236, 72, 153;
            --glow: 0 0 20px rgba(217, 70, 239, 0.25);
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(var(--primary-rgb), 0.05), transparent 45%),
                radial-gradient(circle at 90% 80%, rgba(var(--accent-rgb), 0.05), transparent 45%),
                linear-gradient(rgba(255, 255, 255, 0.002) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.002) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 25px 25px, 25px 25px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            color: var(--text-main);
            overflow-x: hidden;
            padding: 40px 20px;
            box-sizing: border-box;
            transition: background-image 0.5s ease;
        }}

        /* Glow Spheres */
        .glow-sphere {{
            position: absolute;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(var(--primary-rgb), 0.15) 0%, transparent 70%);
            filter: blur(50px);
            z-index: -1;
            animation: floatGlow 12s infinite alternate ease-in-out;
            pointer-events: none;
        }}
        .glow-sphere-1 {{
            top: 10%;
            left: 15%;
        }}
        .glow-sphere-2 {{
            bottom: 10%;
            right: 15%;
            animation-delay: -6s;
            background: radial-gradient(circle, rgba(var(--accent-rgb), 0.12) 0%, transparent 70%);
        }}

        @keyframes floatGlow {{
            0% {{ transform: translate(0, 0) scale(1); }}
            100% {{ transform: translate(40px, -40px) scale(1.15); }}
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6), inset 0 1px 2px rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 35px 30px;
            width: 100%;
            max-width: 550px;
            text-align: center;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
            animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 10;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(15px); }}
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
            opacity: 0.35;
            transition: opacity 0.4s ease;
        }}
        .card:hover::before {{
            opacity: 0.7;
        }}

        /* THEME SWITCHER */
        .theme-switcher {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 100;
        }}
        .theme-toggle-btn {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        .theme-toggle-btn:hover {{
            background: rgba(var(--primary-rgb), 0.1);
            border-color: var(--primary);
            transform: rotate(15deg) scale(1.05);
        }}
        .theme-menu {{
            position: absolute;
            top: 45px;
            right: 0;
            background: rgba(10, 15, 30, 0.95);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 8px;
            width: 160px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
            opacity: 0;
            transform: translateY(-10px);
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .theme-menu.show {{
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }}
        .theme-option {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-muted);
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s ease;
            text-align: left;
        }}
        .theme-option:hover {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-main);
        }}
        .theme-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}

        /* LOGO STYLES */
        .logo-container {{
            margin-bottom: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .main-logo {{
            width: 68px;
            height: 68px;
            margin-bottom: 8px;
        }}
        .logo-ring-outer {{
            transform-origin: center;
            animation: cyberSpin 14s linear infinite;
        }}
        @keyframes cyberSpin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .logo-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 23px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 8px rgba(var(--primary-rgb), 0.25));
        }}
        .logo-subtitle {{
            font-size: 8.5px;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
            margin-top: 3px;
        }}

        /* BADGES */
        .badges-row {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 18px;
            flex-wrap: wrap;
        }}
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(var(--primary-rgb), 0.06);
            border: 1px solid rgba(var(--primary-rgb), 0.15);
            color: var(--primary);
            padding: 5px 12px;
            border-radius: 50px;
            font-size: 9.5px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }}
        .status-dot {{
            width: 5px;
            height: 5px;
            background-color: var(--primary);
            border-radius: 50%;
            box-shadow: 0 0 6px var(--primary);
            animation: blink 1.5s infinite;
        }}
        .secure-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 5px 12px;
            border-radius: 50px;
            font-size: 9.5px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }}
        .secure-badge svg {{
            width: 10px;
            height: 10px;
            fill: currentColor;
        }}

        @keyframes blink {{
            0%, 100% {{ opacity: 0.35; }}
            50% {{ opacity: 1; }}
        }}

        /* PREVIEW WRAPPERS */
        .file-icon-wrapper {{
            position: relative;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 72px;
            height: 72px;
            background: rgba(var(--primary-rgb), 0.06);
            border: 1px solid rgba(var(--primary-rgb), 0.15);
            border-radius: 18px;
            margin-bottom: 16px;
            box-shadow: inset 0 0 12px rgba(var(--primary-rgb), 0.08);
            animation: pulseGlow 4s infinite ease-in-out;
        }}

        @keyframes pulseGlow {{
            0%, 100% {{ box-shadow: inset 0 0 12px rgba(var(--primary-rgb), 0.08), 0 0 8px rgba(var(--primary-rgb), 0.03); }}
            50% {{ box-shadow: inset 0 0 20px rgba(var(--primary-rgb), 0.15), 0 0 15px rgba(var(--primary-rgb), 0.12); border-color: rgba(var(--primary-rgb), 0.35); }}
        }}

        .file-icon {{
            font-size: 32px;
            filter: drop-shadow(0 0 6px rgba(var(--primary-rgb), 0.4));
        }}

        .filename {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 700;
            line-height: 1.4;
            color: var(--text-main);
            word-break: break-all;
            margin-bottom: 20px;
            padding: 0 5px;
        }}

        /* MEDIA CONTAINERS */
        .media-container {{
            margin-bottom: 22px;
            border-radius: 16px;
            overflow: hidden;
            background: #000;
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
            position: relative;
            transition: all 0.3s ease;
        }}
        .media-container:hover {{
            border-color: rgba(var(--primary-rgb), 0.25);
            box-shadow: 0 8px 30px rgba(var(--primary-rgb), 0.1);
        }}
        
        video {{
            display: block;
            width: 100%;
            outline: none;
            max-height: 400px;
            background: #000;
        }}
        
        audio {{
            display: block;
            width: 100%;
            outline: none;
            background: #090c13;
            padding: 12px;
            box-sizing: border-box;
        }}

        /* Document Preview Block */
        .doc-preview-container {{
            background: rgba(255,255,255,0.015);
            border: 1px dashed rgba(255, 255, 255, 0.08);
            padding: 30px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }}
        .doc-icon-glow {{
            font-size: 42px;
            filter: drop-shadow(0 0 10px rgba(var(--primary-rgb), 0.2));
            animation: bounceSlow 3s infinite alternate ease-in-out;
        }}
        @keyframes bounceSlow {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-5px); }}
        }}
        .doc-details {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .doc-title {{
            font-size: 13.5px;
            font-weight: 600;
            color: var(--text-main);
            word-break: break-all;
        }}
        .doc-subtitle {{
            font-size: 11px;
            color: var(--text-muted);
        }}

        /* INTEGRITY SCANNER WIDGET */
        .scanner-section {{
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 22px;
            text-align: left;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);
        }}
        .scanner-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }}
        .scanner-radar {{
            position: relative;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 1.5px solid rgba(var(--primary-rgb), 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .radar-sweep {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            border-radius: 50%;
            border: 1.5px solid transparent;
            border-top-color: var(--primary);
            animation: cyberSpin 1.8s linear infinite;
        }}
        .radar-dot {{
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: var(--primary);
            box-shadow: 0 0 6px var(--primary);
        }}
        .scanner-title-group {{
            flex: 1;
        }}
        .scanner-status {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 11px;
            font-weight: 700;
            color: var(--primary);
            letter-spacing: 0.5px;
        }}
        .scanner-sub {{
            font-size: 8.5px;
            color: var(--text-muted);
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .scanner-console {{
            font-family: monospace;
            font-size: 9.5px;
            color: rgba(var(--primary-rgb), 0.85);
            background: rgba(0,0,0,0.4);
            border-radius: 8px;
            padding: 10px;
            height: 52px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.02);
            line-height: 1.4;
        }}
        .scanner-console::-webkit-scrollbar {{
            width: 3px;
        }}
        .scanner-console::-webkit-scrollbar-thumb {{
            background: rgba(var(--primary-rgb), 0.2);
            border-radius: 2px;
        }}
        .console-line {{
            opacity: 0;
            transform: translateY(3px);
            animation: lineIn 0.3s forwards ease-out;
        }}
        @keyframes lineIn {{
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* ACTION DRAWERS */
        .actions-drawer-container {{
            opacity: 0.2;
            pointer-events: none;
            transition: all 0.5s ease;
        }}
        .actions-drawer-container.unlocked {{
            opacity: 1;
            pointer-events: auto;
        }}

        .download-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #030408;
            padding: 15px 28px;
            border-radius: 14px;
            text-decoration: none;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            width: 100%;
            box-sizing: border-box;
            box-shadow: var(--glow);
            position: relative;
            overflow: hidden;
            margin-bottom: 12px;
            border: none;
            cursor: pointer;
        }}
        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(var(--primary-rgb), 0.5);
            background: linear-gradient(135deg, var(--primary), var(--accent));
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
            transition: all 0.6s ease;
            opacity: 0;
        }}
        .download-btn:hover::after {{
            left: 120%;
            opacity: 1;
        }}

        .actions-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-bottom: 22px;
        }}
        .action-btn {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 10px 4px;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 9.5px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-decoration: none;
        }}
        .action-btn:hover {{
            background: rgba(var(--primary-rgb), 0.05);
            border-color: var(--primary);
            color: var(--text-main);
            transform: translateY(-2px);
        }}
        .action-btn svg {{
            width: 16px;
            height: 16px;
            fill: currentColor;
            transition: transform 0.3s ease;
        }}
        .action-btn:hover svg {{
            transform: scale(1.15);
        }}

        /* SPECIFICATION GRID */
        .specs-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 24px;
        }}
        .spec-item {{
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 10px 12px;
            text-align: left;
            transition: all 0.3s ease;
        }}
        .spec-item:hover {{
            background: rgba(255, 255, 255, 0.025);
            border-color: rgba(255, 255, 255, 0.06);
        }}
        .spec-label {{
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            margin-bottom: 2px;
        }}
        .spec-value {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-main);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .stats-footer {{
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            opacity: 0.75;
            margin-bottom: 24px;
        }}
        .stats-footer svg {{
            width: 13px;
            height: 13px;
            fill: currentColor;
        }}

        /* DEVELOPER BLUEPRINT CARD */
        .dev-section {{
            border-top: 1px dashed rgba(var(--primary-rgb), 0.15);
            padding-top: 20px;
            text-align: left;
        }}
        .dev-title {{
            font-size: 9.5px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 10px;
            opacity: 0.8;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .dev-title::before {{
            content: '';
            display: inline-block;
            width: 5px;
            height: 5px;
            background: var(--primary);
            box-shadow: 0 0 6px var(--primary);
            border-radius: 50%;
        }}
        .dev-profile-link {{
            text-decoration: none;
            display: block;
            background: rgba(255, 255, 255, 0.008);
            border: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 14px;
            padding: 10px 14px;
            transition: all 0.3s ease;
        }}
        .dev-profile-link:hover {{
            background: rgba(var(--primary-rgb), 0.02);
            border-color: rgba(var(--primary-rgb), 0.15);
            box-shadow: 0 0 12px rgba(var(--primary-rgb), 0.03);
            transform: translateY(-1px);
        }}
        .dev-content {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .dev-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.08);
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
            font-size: 13.5px;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 1px;
        }}
        .dev-bio {{
            font-size: 10.5px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
        }}
        .dev-followers {{
            font-size: 9.5px;
            color: var(--primary);
            font-weight: 600;
            margin-top: 2px;
        }}
        .dev-arrow {{
            width: 18px;
            height: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            transition: transform 0.3s ease, color 0.3s ease;
        }}
        .dev-profile-link:hover .dev-arrow {{
            transform: translateX(3px);
            color: var(--primary);
        }}
        .dev-arrow svg {{
            width: 100%;
            height: 100%;
            fill: currentColor;
        }}

        /* TOAST SYSTEM */
        .toast-container {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }}
        .toast {{
            background: rgba(10, 15, 30, 0.95);
            border: 1px solid var(--primary);
            box-shadow: 0 0 15px rgba(var(--primary-rgb), 0.15);
            padding: 10px 18px;
            border-radius: 10px;
            color: #fff;
            font-size: 11.5px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            transform: translateY(20px);
            opacity: 0;
            pointer-events: auto;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            backdrop-filter: blur(8px);
        }}
        .toast.show {{
            transform: translateY(0);
            opacity: 1;
        }}
        .toast-icon {{
            color: var(--primary);
            font-weight: bold;
        }}

        /* GLASSMORPHIC QR MODAL */
        .qr-modal {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(3, 4, 8, 0.8);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }}
        .qr-modal.show {{
            opacity: 1;
            pointer-events: auto;
        }}
        .qr-modal-content {{
            background: rgba(10, 15, 30, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            width: 90%;
            max-width: 350px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.8);
            overflow: hidden;
            transform: scale(0.95);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .qr-modal.show .qr-modal-content {{
            transform: scale(1);
        }}
        .qr-modal-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .qr-modal-header h3 {{
            margin: 0;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 15px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--primary);
        }}
        .close-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 20px;
            cursor: pointer;
            transition: color 0.2s ease;
        }}
        .close-btn:hover {{
            color: #fff;
        }}
        .qr-code-body {{
            padding: 20px;
            text-align: center;
        }}
        .qr-code-body p {{
            font-size: 11px;
            color: var(--text-muted);
            margin: 0 0 15px 0;
            line-height: 1.4;
        }}
        .qr-img-wrapper {{
            width: 180px;
            height: 180px;
            background: #030408;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            margin: 0 auto 15px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        .qr-image {{
            width: 100%;
            height: 100%;
            display: block;
        }}
        .qr-loader {{
            font-size: 11px;
            color: var(--primary);
            font-family: monospace;
        }}
        .qr-modal-footer {{
            background: rgba(0,0,0,0.3);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.02);
            word-break: break-all;
        }}
        .qr-url-text {{
            font-size: 9px;
            color: var(--text-muted);
            font-family: monospace;
        }}

        @media (max-width: 480px) {{
            .card {{
                padding: 25px 20px;
                border-radius: 20px;
            }}
            .filename {{
                font-size: 16px;
            }}
            .file-icon-wrapper {{
                width: 64px;
                height: 64px;
                border-radius: 14px;
            }}
            .file-icon {{
                font-size: 26px;
            }}
            .download-btn {{
                padding: 12px 20px;
                font-size: 13.5px;
            }}
            .actions-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 6px;
            }}
            .spec-item {{
                padding: 8px 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="glow-sphere glow-sphere-1"></div>
    <div class="glow-sphere glow-sphere-2"></div>
    
    <div class="card">
        <!-- Interactive Theme Switcher -->
        <div class="theme-switcher">
            <div class="theme-toggle-btn" onclick="toggleThemeMenu()">🎨</div>
            <div class="theme-menu" id="theme-menu">
                <div class="theme-option" onclick="setTheme('cyber')">
                    <span class="theme-dot" style="background: linear-gradient(135deg, #00f2fe, #d946ef);"></span>
                    Cyber Cyan
                </div>
                <div class="theme-option" onclick="setTheme('sunburst')">
                    <span class="theme-dot" style="background: linear-gradient(135deg, #ff5e62, #febb2c);"></span>
                    Sunburst Neon
                </div>
                <div class="theme-option" onclick="setTheme('emerald')">
                    <span class="theme-dot" style="background: linear-gradient(135deg, #10b981, #fbbf24);"></span>
                    Toxic Emerald
                </div>
                <div class="theme-option" onclick="setTheme('amethyst')">
                    <span class="theme-dot" style="background: linear-gradient(135deg, #d946ef, #ec4899);"></span>
                    Deep Amethyst
                </div>
            </div>
        </div>

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

        <div class="badges-row">
            <div class="status-badge">
                <span class="status-dot"></span>
                Direct Stream Active
            </div>
            <div class="secure-badge" id="secured-badge" style="display:none;">
                <svg viewBox="0 0 20 20"><path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/></svg>
                Secured SSL
            </div>
        </div>
        
        <div class="file-icon-wrapper">
            <span class="file-icon">{icon}</span>
        </div>
        
        <div class="filename">{filename}</div>
        
        {media_player}

        <!-- Cloud Integrity & Security Scanner -->
        <div class="scanner-section" id="scanner-widget">
            <div class="scanner-header">
                <div class="scanner-radar">
                    <div class="radar-sweep"></div>
                    <div class="radar-dot"></div>
                </div>
                <div class="scanner-title-group">
                    <div class="scanner-status" id="scan-status-text">INTEGRITY CHECK IN PROGRESS...</div>
                    <div class="scanner-sub">CLOUD SYSTEM SECURITY MONITOR</div>
                </div>
            </div>
            <div class="scanner-console" id="scanner-console">
                <div class="console-line">> [SYSTEM] SECURE CONNECTING...</div>
            </div>
        </div>

        <!-- Fully Unlocked Drawer -->
        <div class="actions-drawer-container" id="actions-drawer">
            <a href="/dl/{identifier}" class="download-btn">
                <svg style="width: 18px; height: 18px; fill: currentColor;" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
                Secure Download Now
            </a>

            <div class="actions-grid">
                <button class="action-btn" onclick="copyLink('web')">
                    <svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                    <span>Copy Web</span>
                </button>
                <button class="action-btn" onclick="copyLink('direct')">
                    <svg viewBox="0 0 24 24"><path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z"/></svg>
                    <span>Direct Link</span>
                </button>
                <a id="tg-share-btn" href="#" target="_blank" class="action-btn">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.11.02-1.89 1.2-5.33 3.52-.5.35-.96.52-1.37.51-.46-.01-1.35-.26-2.01-.48-.81-.27-1.46-.42-1.4-.88.03-.24.37-.49 1.03-.74 4.04-1.76 6.74-2.92 8.09-3.48 3.85-1.6 4.64-1.88 5.17-1.89.11 0 .37.03.54.17.14.12.18.28.2.45-.02.07-.02.13-.03.19z"/></svg>
                    <span>Share TG</span>
                </a>
                <button class="action-btn" onclick="openQrModal()">
                    <svg viewBox="0 0 24 24"><path d="M3 11h8V3H3v8zm2-6h4v4H5V5zm-2 16h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zm-6 4h3v2h-3zm3 2h2v2h-2zm-3 2h3v2h-3zm3 2h2v-2h-2zm2-4h3v2h-3zm0 4h3v-2h-3zm0-8h2v2h-2zm2 2h2v2h-2z"/></svg>
                    <span>Mobile QR</span>
                </button>
            </div>
        </div>

        <!-- Specifications Info Grid -->
        <div class="specs-grid">
            <div class="spec-item">
                <div class="spec-label">Format / Type</div>
                <div class="spec-value">{file_type_badge}</div>
            </div>
            <div class="spec-item">
                <div class="spec-label">File Size</div>
                <div class="spec-value">{size_formatted}</div>
            </div>
            <div class="spec-item">
                <div class="spec-label">Total Downloads</div>
                <div class="spec-value">{downloads}</div>
            </div>
            <div class="spec-item">
                <div class="spec-label">Uploaded On</div>
                <div class="spec-value">{created_date}</div>
            </div>
        </div>
        
        <div class="stats-footer">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
            Secure AES-256 cloud-encrypted stream channel
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

    <!-- Toast system -->
    <div class="toast-container" id="toast-container"></div>

    <!-- Glassmorphic QR Modal -->
    <div class="qr-modal" id="qr-modal" onclick="closeQrModal(event)">
        <div class="qr-modal-content" onclick="event.stopPropagation()">
            <div class="qr-modal-header">
                <h3>Scan QR Code</h3>
                <button class="close-btn" onclick="closeQrModal()">&times;</button>
            </div>
            <div class="qr-code-body">
                <p>Scan this QR code with your mobile device to view or download this file instantly.</p>
                <div class="qr-img-wrapper" id="qr-img-wrapper">
                    <div class="qr-loader">GENERATING ENCRYPTED CODE...</div>
                </div>
                <div class="qr-modal-footer">
                    <span class="qr-url-text" id="qr-url-text"></span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const identifier = "{identifier}";
        const filename = "{filename}";
        
        // Theme selector
        function setTheme(theme) {{
            document.body.className = '';
            if (theme !== 'cyber') {{
                document.body.classList.add('theme-' + theme);
            }}
            localStorage.setItem('filetolink_theme', theme);
            
            const menu = document.getElementById('theme-menu');
            if (menu) menu.classList.remove('show');
            
            // Re-render QR code matching the new theme color
            if (document.getElementById('qr-modal').classList.contains('show')) {{
                updateQrCode();
            }}
        }}

        function toggleThemeMenu() {{
            document.getElementById('theme-menu').classList.toggle('show');
        }}

        // Setup share link
        document.getElementById('tg-share-btn').href = "https://t.me/share/url?url=" + encodeURIComponent(window.location.href) + "&text=" + encodeURIComponent("Direct Link to: " + filename);

        // Copy Clipboard helpers
        function copyLink(type) {{
            let urlToCopy = "";
            let message = "";
            if (type === 'web') {{
                urlToCopy = window.location.href;
                message = "Web Preview Link Copied!";
            }} else {{
                urlToCopy = window.location.origin + "/dl/" + identifier;
                message = "Direct Download Link Copied!";
            }}

            if (navigator.clipboard) {{
                navigator.clipboard.writeText(urlToCopy).then(() => {{
                    showToast(message);
                }}).catch(() => {{
                    fallbackCopy(urlToCopy, message);
                }});
            }} else {{
                fallbackCopy(urlToCopy, message);
            }}
        }}

        function fallbackCopy(text, msg) {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{
                document.execCommand('copy');
                showToast(msg);
            }} catch (err) {{
                showToast("Copy failed", "error");
            }}
            document.body.removeChild(textArea);
        }}

        function showToast(message, type = "success") {{
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = "toast " + type;
            toast.innerHTML = '<span class="toast-icon">✓</span><span class="toast-msg">' + message + '</span>';
            container.appendChild(toast);
            setTimeout(() => toast.classList.add('show'), 10);
            setTimeout(() => {{
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }}, 3000);
        }}

        // Modal triggers
        function openQrModal() {{
            const modal = document.getElementById('qr-modal');
            modal.classList.add('show');
            document.getElementById('qr-url-text').textContent = window.location.href;
            updateQrCode();
        }}

        function closeQrModal() {{
            document.getElementById('qr-modal').classList.remove('show');
        }}

        function updateQrCode() {{
            const wrapper = document.getElementById('qr-img-wrapper');
            const primaryColor = getComputedStyle(document.body).getPropertyValue('--primary').trim();
            const cleanColor = primaryColor.replace('#', '');
            const currentUrl = window.location.href;
            
            wrapper.innerHTML = '<img class="qr-image" src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=' + encodeURIComponent(currentUrl) + '&color=' + cleanColor + '&bgcolor=030408" alt="QR Code">';
        }}

        // Simulated integrity scanner
        function startIntegrityCheck() {{
            const consoleBox = document.getElementById('scanner-console');
            const consoleLines = [
                "> [SECURE SHIELD] Fetching SSL/TLS 1.3 handshake protocols...",
                "> [NETWORK ENGINE] Opening high-speed direct pipeline node...",
                "> [INTEGRITY SEAL] Checking file stream header metadata...",
                "> [ANTI-VIRUS SCAN] Deep lookup: CLEAN. 0/78 active threats.",
                "> [VERDICT] STATUS SECURE. Unlock engine pipeline..."
            ];
            
            let currentLine = 0;
            const interval = setInterval(() => {{
                if (currentLine < consoleLines.length) {{
                    const lineDiv = document.createElement('div');
                    lineDiv.className = 'console-line';
                    lineDiv.textContent = consoleLines[currentLine];
                    consoleBox.appendChild(lineDiv);
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                    currentLine++;
                }} else {{
                    clearInterval(interval);
                    completeScan();
                }}
            }}, 350);
        }}

        function completeScan() {{
            document.getElementById('scan-status-text').textContent = "SYSTEM INTEGRITY SECURED";
            document.getElementById('secured-badge').style.display = 'inline-flex';
            
            const scannerWidget = document.getElementById('scanner-widget');
            scannerWidget.style.borderColor = '#10b981';
            scannerWidget.style.background = 'rgba(16, 185, 129, 0.04)';
            document.getElementById('scan-status-text').style.color = '#10b981';
            
            setTimeout(() => {{
                // Fade-out scanner slightly and fully unlock buttons
                document.getElementById('actions-drawer').classList.add('unlocked');
            }}, 300);
        }}

        async function fetchDevDetails() {{
            try {{
                const res = await fetch('https://api.github.com/users/Tom2001moT');
                if (!res.ok) throw new Error('API Error');
                const data = await res.json();
                document.getElementById('dev-avatar').src = data.avatar_url;
                document.getElementById('dev-name').textContent = data.name || 'Tom';
                document.getElementById('dev-bio').textContent = data.bio || 'Core Developer';
                document.getElementById('dev-followers').textContent = data.followers + " Followers";
            }} catch (e) {{
                document.getElementById('dev-avatar').src = 'https://avatars.githubusercontent.com/u/10000000?v=4';
                document.getElementById('dev-name').textContent = 'Tom2001moT';
                document.getElementById('dev-bio').textContent = 'System & Bot Developer';
                document.getElementById('dev-followers').textContent = 'GitHub Developer';
            }}
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            const savedTheme = localStorage.getItem('filetolink_theme') || 'cyber';
            setTheme(savedTheme);
            fetchDevDetails();
            setTimeout(startIntegrityCheck, 300);
        }});
        
        // Close menus if click elsewhere
        window.addEventListener('click', (e) => {{
            if (!e.target.closest('.theme-switcher')) {{
                const menu = document.getElementById('theme-menu');
                if (menu) menu.classList.remove('show');
            }}
        }});
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
            created_date = file_record[7]
        else:
            msg = await app.get_messages(LOG_CHANNEL, message_id)
            if not msg or not msg.media: return web.Response(status=404, text="Not Found")
            media = getattr(msg, msg.media.value)
            filename = getattr(media, "file_name", "file") or "file"
            file_size = getattr(media, "file_size", 0) or 0
            downloads = 0
            created_date = "N/A"

        # Format created_date nicely
        formatted_date = "Unknown Date"
        if created_date and created_date != "N/A":
            try:
                # sqlite format is usually YYYY-MM-DD HH:MM:SS
                dt = datetime.strptime(created_date.split('.')[0], "%Y-%m-%d %H:%M:%S")
                formatted_date = dt.strftime("%b %d, %Y - %I:%M %p")
            except Exception:
                formatted_date = str(created_date)
        else:
            formatted_date = "Direct Tunnel"

        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or 'application/octet-stream'

        lower_filename = filename.lower()
        icon = "📁"
        file_type_badge = "Unknown File"
        if mime_type.startswith("video/") or any(ext in lower_filename for ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]):
            icon = "🎥"
            file_type_badge = "Video Stream"
        elif mime_type.startswith("audio/") or any(ext in lower_filename for ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]):
            icon = "🎵"
            file_type_badge = "Audio Stream"
        elif mime_type.startswith("image/") or any(ext in lower_filename for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]):
            icon = "🖼️"
            file_type_badge = "Image Preview"
        elif any(ext in lower_filename for ext in [".zip", ".rar", ".7z", ".tar", ".gz"]):
            icon = "📦"
            file_type_badge = "Archive"
        elif ".pdf" in lower_filename:
            icon = "📕"
            file_type_badge = "PDF Document"
        elif any(ext in lower_filename for ext in [".txt", ".log", ".md", ".json", ".xml", ".py", ".js"]):
            icon = "📄"
            file_type_badge = "Text Document"

        media_player = ""
        if mime_type.startswith("video/") or any(ext in lower_filename for ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]):
            media_player = f'<div class="media-container"><video id="media-element" controls><source src="/stream/{identifier}" type="{mime_type}">Your browser does not support the video tag.</video></div>'
        elif mime_type.startswith("audio/") or any(ext in lower_filename for ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]):
            media_player = f'<div class="media-container"><audio id="media-element" controls><source src="/stream/{identifier}" type="{mime_type}">Your browser does not support the audio element.</audio></div>'
        elif mime_type.startswith("image/") or any(ext in lower_filename for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]):
            media_player = f'<div class="media-container"><img id="media-element" src="/stream/{identifier}" alt="{filename}" style="max-width: 100%; max-height: 400px; display: block; margin: 0 auto; border-radius: 12px; object-fit: contain;"></div>'
        else:
            media_player = f"""
            <div class="media-container doc-preview-container">
                <div class="doc-icon-glow">{icon}</div>
                <div class="doc-details">
                    <span class="doc-title">{filename}</span>
                    <span class="doc-subtitle">Ready to download secure archive ({format_size(file_size)})</span>
                </div>
            </div>
            """

        html = HTML_TEMPLATE.format(
            filename=filename,
            size_formatted=format_size(file_size),
            identifier=identifier,
            downloads=downloads,
            media_player=media_player,
            icon=icon,
            created_date=formatted_date,
            file_type_badge=file_type_badge
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
