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
    LOG_CHANNEL = 0 

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
        if not msg or not msg.media: return web.Response(status=404, text="File Not Found")
        
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "unknown") or "file"
        
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(media.file_size)
        })
        await response.prepare(request)
        async for chunk in app.stream_media(msg): await response.write(chunk)
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
                
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" not in update: continue
                    
                    message = update["message"]
                    chat_id = message["chat"]["id"]
                    text = message.get("text", "")
                    
                    # --- ID DETECTOR LOGIC ---
                    # If user forwards a message from a channel, tell them the ID
                    if "forward_from_chat" in message:
                        fwd_id = message["forward_from_chat"]["id"]
                        fwd_title = message["forward_from_chat"]["title"]
                        await app.send_message(chat_id, f"📢 **Channel Detected!**\n\n**Name:** {fwd_title}\n**ID:** `{fwd_id}`\n\nCopy this ID to Render LOG_CHANNEL variable!")
                        continue

                    # Handle /start
                    if text.startswith("/start"):
                        await app.send_message(chat_id, "👋 **Bot is Online!**\n\n1. Forward a message from your Log Channel to get the correct ID.\n2. Or send me a file to convert.")
                        continue
                    
                    if not any(key in message for key in ["document", "video", "audio", "photo"]):
                        continue

                    # Process File
                    status_msg = await app.send_message(chat_id, "🔄 **Processing...**")
                    try:
                        # Attempt to resolve peer if ID is valid
                        try:
                            # Try to see the channel first to cache it
                            await app.get_chat(LOG_CHANNEL)
                        except:
                            pass # Continue anyway, maybe it's already cached

                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, message["message_id"])
                        
                        link = f"{os.environ.get('RENDER_EXTERNAL_URL', f'http://localhost:{PORT}')}/dl/{log_msg.id}"
                        filename = "file"
                        if log_msg.document: filename = log_msg.document.file_name
                        elif log_msg.video: filename = log_msg.video.file_name
                        
                        await app.edit_message_text(
                            chat_id, status_msg.id,
                            f"✅ **File Saved!**\n\n📂 **Name:** `{filename}`\n🔗 **Link:**\n{link}"
                        )
                    except Exception as e:
                        err = str(e)
                        if "PEER_ID_INVALID" in err.upper():
                            await app.edit_message_text(chat_id, status_msg.id, f"❌ **ID Error:** The Log Channel ID `{LOG_CHANNEL}` is invalid or the bot hasn't met the channel.\n\n**FIX:** Forward a message from the channel to this bot right now!")
                        else:
                            await app.edit_message_text(chat_id, status_msg.id, f"❌ Error: {e}")

            except Exception as e:
                print(f"Polling Exception: {e}")
                await asyncio.sleep(5)

# --- MAIN EXECUTION ---
async def start_services():
    print("--- Starting Pyrogram ---")
    await app.start()
    
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
