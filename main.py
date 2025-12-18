
import os
import asyncio
import logging
import aiohttp
from pyrogram import Client
from aiohttp import web

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL_RAW = os.environ.get("LOG_CHANNEL", "0")
PORT = int(os.environ.get("PORT", 8080))

# Sanitize Channel ID
try:
    LOG_CHANNEL = int(LOG_CHANNEL_RAW)
except ValueError:
    LOG_CHANNEL = 0 # Invalid ID

# --- PYROGRAM CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- WEB SERVER HANDLERS ---
async def handle_stream(request):
    try:
        message_id = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        
        if not msg or not msg.media:
            return web.Response(status=404, text="File Not Found or No Media")
        
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "unknown_file") or "file"
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(media.file_size)
        })
        await response.prepare(request)
        
        async for chunk in app.stream_media(msg):
            await response.write(chunk)
            
        return response
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")

async def health_check(request):
    return web.Response(text="Bot is running")

# --- MANUAL HTTP POLLING ---
async def start_polling():
    print("--- 🚀 Starting Hybrid HTTP Poller ---")
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, params={"offset": offset, "timeout": 10}) as resp:
                    data = await resp.json()
                    
                if not data.get("ok"):
                    await asyncio.sleep(5)
                    continue
                
                updates = data.get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    if "message" not in update: continue
                    
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    print(f"DEBUG: Fetched message from {chat_id}")

                    # Handle /start
                    if text.startswith("/start"):
                        await app.send_message(chat_id, "👋 **Bot is Online!**\nSend me a file.")
                        continue
                    
                    # Handle Media
                    if not any(key in message for key in ["document", "video", "audio", "photo"]):
                        await app.send_message(chat_id, "❌ Please send a file, video, or photo.")
                        continue

                    # Process File
                    status_msg = await app.send_message(chat_id, "🔄 **Processing...**")
                    try:
                        # Copy to Log Channel
                        log_msg = await app.copy_message(
                            chat_id=LOG_CHANNEL,
                            from_chat_id=chat_id,
                            message_id=message["message_id"]
                        )
                        
                        base_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
                        stream_link = f"{base_url}/dl/{log_msg.id}"
                        
                        filename = "file"
                        if log_msg.document: filename = log_msg.document.file_name
                        elif log_msg.video: filename = log_msg.video.file_name
                        elif log_msg.audio: filename = log_msg.audio.file_name
                        
                        await app.edit_message_text(
                            chat_id=chat_id,
                            message_id=status_msg.id,
                            text=f"✅ **File Saved!**\n\n📂 **Name:** `{filename}`\n🔗 **Link:**\n{stream_link}"
                        )
                    except Exception as e:
                        print(f"Processing Error: {e}")
                        # If Peer ID Invalid, inform user
                        err_msg = str(e)
                        if "PEER_ID_INVALID" in err_msg.upper():
                             await app.edit_message_text(chat_id, status_msg.id, f"❌ Error: Bot cannot access Log Channel ({LOG_CHANNEL}). Ensure Bot is ADMIN and ID is correct.")
                        else:
                             await app.edit_message_text(chat_id, status_msg.id, f"❌ Error: {e}")

            except Exception as e:
                print(f"Polling Exception: {e}")
                await asyncio.sleep(5)

# --- MAIN EXECUTION ---
async def start_services():
    print("--- Starting Pyrogram Client ---")
    await app.start()
    print("--- Pyrogram Started ---")
    
    # --- CRITICAL FIX: Force-Resolve Channel ---
    # This step ensures the bot "knows" the channel before trying to copy to it
    try:
        print(f"--- Resolving Log Channel: {LOG_CHANNEL} ---")
        chat = await app.get_chat(LOG_CHANNEL)
        print(f"--- Success! Found Channel: {chat.title} (ID: {chat.id}) ---")
    except Exception as e:
        print(f"--- WARNING: Could not resolve Log Channel: {e} ---")
        print("--- Make sure the Bot is an ADMIN in the channel! ---")

    print("--- Starting Web Server ---")
    server = web.Application()
    server.router.add_get('/', health_check)
    server.router.add_get('/dl/{id}', handle_stream)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"--- Web Server running on port {PORT} ---")

    await start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
