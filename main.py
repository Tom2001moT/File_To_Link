import os
import asyncio
import urllib.request
import json
from pyrogram import Client, filters
from aiohttp import web

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
PORT = int(os.environ.get("PORT", 8080))

# --- HELPER: CLEAR WEBHOOK ---
def nuke_webhook():
    print("--- 🧹 Clearing Zombie Webhooks... ---")
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True"
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
            print(f"--- Webhook Reset Result: {data} ---")
    except Exception as e:
        print(f"--- ⚠️ Webhook Reset Failed: {e} ---")

# --- INITIALIZE CLIENT ---
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    ipv6=False
)

# --- DEBUG HANDLER ---
@app.on_message(group=-1)
async def debug_logger(client, message):
    print(f"DEBUG: Received message from {message.chat.id}")

# --- BOT HANDLERS ---
@app.on_message(filters.command("start"))
async def start_command(client, message):
    print("DEBUG: Sending /start reply")
    await message.reply_text("👋 **Bot is Online!**\nSend me a file to get a link.")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_file(client, message):
    print(f"DEBUG: Processing file from {message.chat.id}")
    status_msg = await message.reply_text("🔄 **Processing...**", quote=True)
    
    try:
        log_msg = await message.copy(chat_id=LOG_CHANNEL)
        file_id = log_msg.id
        
        base_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
        stream_link = f"{base_url}/dl/{file_id}"
        
        await status_msg.edit_text(
            f"✅ **File Saved!**\n\n"
            f"📂 **Name:** `{get_filename(log_msg)}`\n"
            f"🔗 **Download Link:**\n{stream_link}"
        )
    except Exception as e:
        print(f"ERROR: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

def get_filename(msg):
    if msg.document: return msg.document.file_name
    if msg.video: return msg.video.file_name or "video.mp4"
    if msg.audio: return msg.audio.file_name or "audio.mp3"
    if msg.photo: return "photo.jpg"
    return "unknown_file"

# --- WEB SERVER ---
async def handle_stream(request):
    try:
        message_id = int(request.match_info['id'])
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        if not msg or msg.empty: return web.Response(status=404, text="404: File not found")
        
        media = getattr(msg, msg.media.value) if msg.media else None
        if not media: return web.Response(status=404, text="404: No media")

        headers = {
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{get_filename(msg)}"',
            'Content-Length': str(media.file_size)
        }
        response = web.StreamResponse(status=200, headers=headers)
        await response.prepare(request)
        async for chunk in app.stream_media(msg):
            await response.write(chunk)
        return response
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")

async def health_check(request):
    return web.Response(text="Bot is running")

# --- MAIN LOOP ---
async def start_services():
    # 1. Nuke Webhook BEFORE starting Pyrogram
    nuke_webhook()
    
    print("--- Starting Bot ---")
    await app.start()
    print(f"--- Bot Logged In as @{(await app.get_me()).username} ---")

    print("--- Starting Web Server ---")
    server = web.Application()
    server.router.add_get('/', health_check)
    server.router.add_get('/dl/{id}', handle_stream)

    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"--- Web Server running on port {PORT} ---")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
