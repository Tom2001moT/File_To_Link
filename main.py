import os
import asyncio
from pyrogram import Client, filters, enums
from aiohttp import web

# --- CONFIGURATION ---
# Load env vars with defaults to prevent crash on missing keys
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
# Default LOG_CHANNEL to 0 to catch errors later if not set
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
PORT = int(os.environ.get("PORT", 8080))

# Initialize Client
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False  # Important for Render
)

# --- DEBUG LOGGER ---
# Logs every incoming update to help debug silent failures
@app.on_message(group=-1)
async def debug_logger(client, message):
    print(f"DEBUG: Received message from {message.chat.id} | Type: {message.media or 'Text'}")

# --- BOT COMMANDS ---

@app.on_message(filters.command("start"))
async def start_command(client, message):
    print("DEBUG: Sending Start Response")
    await message.reply_text(
        "👋 **Hello!**\n\n"
        "Send me any file (Video, Audio, Document), and I will generate a direct download link for it.\n"
        "🚀 Works for files up to 2GB."
    )

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_file(client, message):
    print(f"DEBUG: Processing file from {message.chat.id}")
    
    # 1. Validation: Check if Log Channel is set
    if LOG_CHANNEL == 0:
        await message.reply_text("❌ **Error:** LOG_CHANNEL ID is missing in server configuration.")
        return

    status_msg = await message.reply_text("🔄 **Processing...**", quote=True)
    
    try:
        # 2. Forward to Log Channel (Critical Step)
        log_msg = await message.copy(chat_id=LOG_CHANNEL)
        file_id = log_msg.id
        
        # 3. Generate Link
        # Render provides RENDER_EXTERNAL_URL. If missing, default to localhost.
        # Format: https://your-app.onrender.com
        base_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
        stream_link = f"{base_url}/dl/{file_id}"
        
        filename = get_filename(log_msg)
        
        await status_msg.edit_text(
            f"✅ **File Saved!**\n\n"
            f"📂 **Name:** `{filename}`\n"
            f"🔗 **Download Link:**\n{stream_link}\n\n"
            f"⚠️ *Note: This link streams directly from Telegram.*"
        )
        
    except Exception as e:
        print(f"ERROR: {e}")
        # Send a user-friendly error message
        error_text = str(e)
        if "CHAT_WRITE_FORBIDDEN" in error_text:
            await status_msg.edit_text("❌ **Error:** Bot is not an Admin in the Log Channel.")
        elif "PEER_ID_INVALID" in error_text:
            await status_msg.edit_text("❌ **Error:** Log Channel ID is incorrect. Make sure it starts with -100.")
        else:
            await status_msg.edit_text(f"❌ **Error:** {error_text}")

def get_filename(msg):
    """Safely extract filename from various media types"""
    if msg.document: 
        return msg.document.file_name or "document.bin"
    if msg.video: 
        return msg.video.file_name or "video.mp4"
    if msg.audio: 
        return msg.audio.file_name or "audio.mp3"
    if msg.photo: 
        return "photo.jpg"
    return "unknown_file"

# --- WEB SERVER HANDLERS ---

async def handle_stream(request):
    try:
        message_id_str = request.match_info['id']
        if not message_id_str.isdigit():
             return web.Response(status=400, text="400: Invalid ID")
             
        message_id = int(message_id_str)
        
        # Fetch message from Log Channel
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        
        if not msg or msg.empty or msg.service:
            return web.Response(status=404, text="404: File not found")

        media = getattr(msg, msg.media.value) if msg.media else None
        if not media:
             return web.Response(status=404, text="404: No media found in this message")

        file_name = get_filename(msg)
        file_size = media.file_size
        mime_type = getattr(media, "mime_type", "application/octet-stream")

        headers = {
            'Content-Type': mime_type,
            'Content-Disposition': f'attachment; filename="{file_name}"',
            'Content-Length': str(file_size)
        }

        response = web.StreamResponse(status=200, headers=headers)
        await response.prepare(request)

        # Stream chunk by chunk
        async for chunk in app.stream_media(msg):
            await response.write(chunk)

        return response

    except Exception as e:
        print(f"STREAM ERROR: {e}")
        return web.Response(status=500, text=f"Server Error: {str(e)}")

async def health_check(request):
    return web.Response(text="Bot is running!")

# --- MAIN EXECUTION ---

async def start_services():
    print("--- Starting Bot ---")
    await app.start()
    
    try:
        me = await app.get_me()
        print(f"--- Bot Logged In as @{me.username} ---")
    except Exception as e:
        print(f"--- FATAL: Bot failed to log in. Check Token/API Keys. Error: {e} ---")
        return

    print("--- Starting Web Server ---")
    server = web.Application()
    server.router.add_get('/', health_check)
    server.router.add_get('/dl/{id}', handle_stream)

    runner = web.AppRunner(server)
    await runner.setup()
    
    # Bind to 0.0.0.0 to be accessible externally
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"--- Web Server running on port {PORT} ---")
    
    # Prevent script from exiting
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
