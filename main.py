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
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
PORT = int(os.environ.get("PORT", 8080))

# --- PYROGRAM CLIENT ---
# We use this for heavy lifting (copying/streaming)
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
        # Fetch message using Pyrogram
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        
        if not msg or not msg.media:
            return web.Response(status=404, text="File Not Found or No Media")
        
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "unknown_file") or "file"
        file_size = getattr(media, "file_size", 0)
        mime_type = getattr(media, "mime_type", "application/octet-stream")
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': mime_type,
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(file_size)
        })
        await response.prepare(request)
        
        # Stream using Pyrogram
        async for chunk in app.stream_media(msg):
            await response.write(chunk)
            
        return response
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")

async def health_check(request):
    return web.Response(text="Bot is running")

# --- MANUAL HTTP POLLING (The Fix) ---
async def start_polling():
    print("--- 🚀 Starting Hybrid HTTP Poller ---")
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # 1. Fetch Updates via HTTP (Bypasses Pyrogram's listener)
                async with session.get(url, params={"offset": offset, "timeout": 10}) as resp:
                    data = await resp.json()
                    
                if not data.get("ok"):
                    print(f"Polling Error: {data}")
                    await asyncio.sleep(5)
                    continue
                
                updates = data.get("result", [])
                
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    if "message" not in update:
                        continue
                        
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    print(f"DEBUG: Fetched message from {chat_id}")

                    # 2. Handle /start
                    if text.startswith("/start"):
                        await app.send_message(chat_id, "👋 **Bot is Online!**\nSend me a file.")
                        continue
                    
                    # 3. Handle Media
                    # Check if message has media keys
                    if not any(key in message for key in ["document", "video", "audio", "photo"]):
                        await app.send_message(chat_id, "❌ Please send a file, video, or photo.")
                        continue

                    # 4. Process Logic (Using Pyrogram for actions)
                    status_msg = await app.send_message(chat_id, "🔄 **Processing...**")
                    
                    try:
                        # Copy from User -> Log Channel
                        # We use the message_id from the HTTP update
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
                        await app.edit_message_text(chat_id, status_msg.id, f"❌ Error: {e}")

            except Exception as e:
                print(f"Polling Exception: {e}")
                await asyncio.sleep(5)

# --- MAIN EXECUTION ---
async def start_services():
    print("--- Starting Pyrogram Client ---")
    await app.start()
    print("--- Pyrogram Started ---")

    print("--- Starting Web Server ---")
    server = web.Application()
    server.router.add_get('/', health_check)
    server.router.add_get('/dl/{id}', handle_stream)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"--- Web Server running on port {PORT} ---")

    # Start the hybrid polling loop
    await start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
