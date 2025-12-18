import os
import asyncio
from pyrogram import Client, filters, enums
from aiohttp import web

# --- CONFIGURATION (Load from Environment Variables) ---
# You will set these in your Render Dashboard later
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0")) # ID of your private channel
PORT = int(os.environ.get("PORT", 8080))

# Initialize Telegram Client
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# --- DEBUG LOGGER ---
# This handler runs for EVERY message to check if the bot is hearing anything.
@app.on_message(group=-1)
async def debug_logger(client, message):
    print(f"DEBUG: Received message from {message.chat.id}: {message.text or 'Media File'}")

# --- TELEGRAM BOT LOGIC ---

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **Hello!**\n\n"
        "Send me any file (Video, Audio, Document), and I will generate a direct download link for it.\n"
        "This works for files up to 2GB (or 4GB for Premium)."
    )

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_file(client, message):
    status_msg = await message.reply_text("🔄 **Processing...**", quote=True)
    
    try:
        # 1. Forward the file to the Log Channel to store it permanently
        # This returns the forwarded message object in the channel
        log_msg = await message.copy(chat_id=LOG_CHANNEL)
        
        # 2. Generate the Link
        # We use the Log Channel Message ID as the unique identifier
        file_id = log_msg.id
        
        # Get the App URL (You'll get this from Render after deployment)
        # Fallback to localhost if not set
        app_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
        stream_link = f"{app_url}/dl/{file_id}"
        
        await status_msg.edit_text(
            f"✅ **File Saved!**\n\n"
            f"📂 **Name:** `{get_filename(log_msg)}`\n"
            f"🔗 **Download Link:**\n{stream_link}\n\n"
            f"⚠️ *Note: This link streams directly from Telegram.*"
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

def get_filename(msg):
    """Helper to extract filename from any media type"""
    if msg.document: return msg.document.file_name
    if msg.video: return msg.video.file_name or "video.mp4"
    if msg.audio: return msg.audio.file_name or "audio.mp3"
    if msg.photo: return "photo.jpg"
    return "unknown_file"

# --- WEB SERVER LOGIC (Aiohttp) ---

async def handle_stream(request):
    try:
        # Extract the message ID from the URL
        message_id = int(request.match_info['id'])
        
        # Fetch the message from the Log Channel
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        
        if not msg or msg.empty or msg.service:
            return web.Response(status=404, text="404: File not found")

        # Determine file details
        media = getattr(msg, msg.media.value) if msg.media else None
        if not media:
             return web.Response(status=404, text="404: No media found in this message")

        file_name = get_filename(msg)
        file_size = media.file_size
        mime_type = getattr(media, "mime_type", "application/octet-stream")

        # Set headers for the browser
        headers = {
            'Content-Type': mime_type,
            'Content-Disposition': f'attachment; filename="{file_name}"',
            'Content-Length': str(file_size)
        }

        # Create the stream response
        response = web.StreamResponse(status=200, headers=headers)
        await response.prepare(request)

        # Stream the file chunk by chunk from Telegram -> Server -> User
        # This keeps RAM usage low even for 2GB files
        async for chunk in app.stream_media(msg):
            await response.write(chunk)

        return response

    except Exception as e:
        return web.Response(status=500, text=f"Server Error: {str(e)}")

async def health_check(request):
    return web.Response(text="Bot is running!")

# --- MAIN EXECUTION ---

async def start_services():
    print("--- Starting Bot ---")
    await app.start()
    print("--- Bot Started. Starting Web Server ---")

    # Setup Web Server
    server = web.Application()
    server.router.add_get('/', health_check)      # Health check for uptime monitors
    server.router.add_get('/dl/{id}', handle_stream) # Download route

    runner = web.AppRunner(server)
    await runner.setup()
    
    # Bind to the port provided by Render (or 8080 default)
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"--- Web Server running on port {PORT} ---")
    
    # Keep the program running indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass,
