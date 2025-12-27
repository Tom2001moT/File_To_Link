# File To Link Bot 🔗

A powerful Telegram bot that converts files into direct download links with 24/7 uptime. Send any file (video, audio, document, photo) to the bot and get an instant shareable download link!

## ✨ Features

- 📤 **Upload Any File**: Supports videos, audio files, documents, and photos
- 🔗 **Direct Download Links**: Generates instant shareable download links
- 💾 **Large File Support**: Handles files up to 2GB (4GB for Telegram Premium users)
- 🚀 **Efficient Streaming**: Uses chunk-by-chunk streaming to minimize RAM usage
- ⚡ **Fast & Reliable**: Built with async/await for optimal performance
- 🔒 **Secure Storage**: Files are stored in your private Telegram channel
- 🌐 **24/7 Uptime**: Self-ping mechanism keeps the bot alive on free hosting
- 📊 **Status Monitoring**: Real-time uptime tracking and system status
- 🔄 **Hybrid Polling**: Custom polling system that handles both commands and files

## 🛠️ Tech Stack

- **Python 3.7+**: Core programming language
- **Pyrogram 2.0.106**: Modern Telegram Bot API framework for MTProto protocol
- **Aiohttp 3.9.1**: Asynchronous HTTP server for file streaming
- **TgCrypto 1.2.5**: Cryptographic library for fast Telegram encryption

## 📋 Prerequisites

Before you begin, you'll need:

1. **Telegram Account** - To create a bot and API credentials
2. **API Credentials from my.telegram.org**:
   - **API ID**: Integer identifier for your application
   - **API Hash**: String hash for authentication
3. **Bot Token from @BotFather**: Your bot's authentication token
4. **Private Channel**: A Telegram channel to store files (must be private for security)
5. **Hosting Platform**: Render.com (free tier) or any Python-supporting platform

### Why You Need Each Component

- **API ID & Hash**: Required for Pyrogram to use Telegram's MTProto protocol
- **Bot Token**: Authenticates your bot with Telegram's Bot API
- **Private Channel**: Acts as free unlimited file storage for your links
- **Hosting**: Runs your bot 24/7 (Render free tier perfect for this)

## 🚀 Quick Start Guide

### Step 1: Get Telegram API Credentials

1. Visit [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Navigate to **"API Development Tools"**
4. Click **"Create New Application"**
5. Fill in application details:
   - **App title**: "File To Link Bot" (or any name)
   - **Short name**: "filetolink" (or any short name)
   - **Platform**: Select "Other"
6. Click **"Create"**
7. Copy your **`API_ID`** (number) and **`API_HASH`** (string)
8. **Keep these secret!** Never share or commit to GitHub

### Step 2: Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start chat and send `/newbot` command
3. Follow the prompts:
   - **Bot name**: "My File To Link Bot" (display name, can include spaces)
   - **Username**: "myfiletolink_bot" (must end with 'bot', no spaces)
4. Copy the **`BOT_TOKEN`** (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. **Keep this secret!** Anyone with token can control your bot

### Step 3: Create Private Channel for File Storage

1. Open Telegram and create a **New Channel**
2. Set channel as **Private** (important for security)
3. Choose a name (e.g., "File Storage")
4. **Add your bot as administrator**:
   - Click channel name → Administrators → Add Administrator
   - Search for your bot username
   - Grant "Post Messages" permission (minimum required)

### Step 4: Get Your Channel ID

**Method 1 (Using another bot - Easiest):**
1. Forward any message from your channel to [@userinfobot](https://t.me/userinfobot)
2. It will reply with the channel ID (e.g., `-1001234567890`)
3. Copy this ID (including the minus sign)

**Method 2 (Using your bot - After deployment):**
1. Deploy your bot (see deployment steps below)
2. Forward any message from your channel to your bot
3. Your bot will reply with the channel ID
4. Update environment variables with this ID

### Step 5: Local Installation & Testing

```bash
# Clone the repository
git clone https://github.com/Tom2001moT/File_To_Link.git
cd File_To_Link

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (Linux/Mac)
export API_ID="your_api_id_here"
export API_HASH="your_api_hash_here"
export BOT_TOKEN="your_bot_token_here"
export LOG_CHANNEL="-1001234567890"
export PORT="8080"
export RENDER_EXTERNAL_URL="http://localhost:8080"

# For Windows (Command Prompt)
set API_ID=your_api_id_here
set API_HASH=your_api_hash_here
set BOT_TOKEN=your_bot_token_here
set LOG_CHANNEL=-1001234567890
set PORT=8080
set RENDER_EXTERNAL_URL=http://localhost:8080

# For Windows (PowerShell)
$env:API_ID="your_api_id_here"
$env:API_HASH="your_api_hash_here"
$env:BOT_TOKEN="your_bot_token_here"
$env:LOG_CHANNEL="-1001234567890"
$env:PORT="8080"
$env:RENDER_EXTERNAL_URL="http://localhost:8080"

# Run the bot
python main.py

# You should see output like:
# --- 🤖 Starting Telegram Client ---
# --- 🔎 Attempting to resolve Log Channel: -1001234567890 ---
# --- ✅ Log Channel Resolved: File Storage ---
# --- 🌐 Web Server running on port 8080 ---
# --- ⏰ Starting 24/7 Keep-Alive for http://localhost:8080 ---
# --- 🚀 Starting Hybrid Update Poller ---
```

### Step 6: Test Your Bot Locally

1. **Open your bot in Telegram** (search for your bot username)
2. **Send `/start` command** - You should get a welcome message
3. **Send `/status` command** - Check if bot is online
4. **Upload a test file** (any small file)
5. **Receive download link** - Try clicking it to download
6. **Test the link in browser** - Visit the link to verify download works

If everything works locally, proceed to deployment!

## ☁️ Production Deployment on Render.com

### Why Render?
- **Free Tier Available**: Perfect for personal projects
- **Automatic Deployments**: Deploys from GitHub automatically
- **Environment Variables**: Easy configuration management
- **24/7 Uptime**: With keep-alive mechanism included in bot
- **No Credit Card**: Free tier doesn't require payment info

### Deployment Steps

#### Step 1: Prepare Your Repository

1. **Fork this repository** to your GitHub account
   - Visit [github.com/Tom2001moT/File_To_Link](https://github.com/Tom2001moT/File_To_Link)
   - Click **"Fork"** button (top right)
   - Wait for fork to complete

2. **(Optional) Clone your fork locally for modifications:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/File_To_Link.git
   cd File_To_Link
   ```

#### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **"Get Started"**
3. Sign up with **GitHub** (recommended for easy deployment)
4. Authorize Render to access your repositories

#### Step 3: Create New Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your forked repository:
   - Click **"Connect GitHub"** if not already connected
   - Find your **"File_To_Link"** repository
   - Click **"Connect"**

#### Step 4: Configure Service Settings

Fill in the following:

**Basic Settings:**
- **Name**: `file-to-link-bot` (or any unique name)
- **Region**: Choose closest to your location
- **Branch**: `main` (or `master`)
- **Root Directory**: Leave blank
- **Runtime**: **Python 3**

**Build Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

**Instance Settings:**
- **Instance Type**: **Free** (sufficient for personal use)

#### Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Key | Value | Description |
|-----|-------|-------------|
| `API_ID` | `12345678` | Your Telegram API ID (integer) |
| `API_HASH` | `your_hash_here` | Your Telegram API Hash (string) |
| `BOT_TOKEN` | `123456:ABCdef...` | Your bot token from BotFather |
| `LOG_CHANNEL` | `-1001234567890` | Your private channel ID (with minus) |
| `PORT` | `8080` | HTTP server port (Render sets this automatically) |

**Important Notes:**
- Don't add `RENDER_EXTERNAL_URL` yet - we'll add it after first deployment
- Make sure `LOG_CHANNEL` includes the minus sign for channel IDs
- Double-check all values - typos will cause errors

#### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start your bot
   - Provide you with a public URL
3. Wait for deployment (usually 2-5 minutes)
4. Check logs for any errors

#### Step 7: Configure External URL

1. After deployment, copy your service URL:
   - Format: `https://your-service-name.onrender.com`
2. Go to **Environment** tab in Render dashboard
3. Add new environment variable:
   - **Key**: `RENDER_EXTERNAL_URL`
   - **Value**: Your service URL (e.g., `https://file-to-link-bot.onrender.com`)
4. Click **"Save Changes"**
5. Service will automatically redeploy

#### Step 8: Verify Deployment

1. **Check Logs** in Render dashboard:
   ```
   --- 🤖 Starting Telegram Client ---
   --- ✅ Log Channel Resolved: Your Channel Name ---
   --- 🌐 Web Server running on port 8080 ---
   --- ⏰ Starting 24/7 Keep-Alive ---
   --- 🚀 Starting Hybrid Update Poller ---
   ```

2. **Test Health Endpoint**:
   - Visit: `https://your-service.onrender.com/`
   - Should show: "Bot is running 24/7" with uptime

3. **Test Bot Commands**:
   - Open your bot in Telegram
   - Send `/start` - Should get welcome message
   - Send `/status` - Should show "Online" with uptime

4. **Test File Upload**:
   - Send any file to your bot
   - Should receive download link
   - Click link to verify download works

### Maintaining 24/7 Uptime

The bot includes built-in keep-alive system, but for extra reliability:

**Option 1: Use UptimeRobot (Recommended)**
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up for free account
3. Add **New Monitor**:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: "File To Link Bot"
   - **URL**: Your Render service URL
   - **Monitoring Interval**: 5 minutes
4. UptimeRobot will ping your bot every 5 minutes

**Option 2: Use Cron-Job.org**
1. Go to [cron-job.org](https://cron-job.org)
2. Create free account
3. Create **New Cronjob**:
   - **URL**: Your Render service URL
   - **Interval**: Every 10 minutes
   - **Save**

**Why Both Internal and External Keep-Alive?**
- **Internal** (in code): Pings itself every 10 minutes
- **External** (UptimeRobot): Backup in case internal fails
- **Together**: Ensures maximum uptime on free tier

## 📖 Bot Usage Guide

### Available Commands

| Command | Description | Example Response |
|---------|-------------|-----------------|
| `/start` | Welcome message and instructions | Shows bot features and usage guide |
| `/help` | Detailed help on how to use the bot | Step-by-step file upload instructions |
| `/status` | Check bot status and uptime | Online status, uptime, server info |
| `/about` | Information about the bot | Developer info and bot purpose |

### How to Use the Bot

#### 1. Starting the Bot

Send `/start` to your bot:

```
You: /start

Bot: 👋 **Welcome to FileToLink Bot!**

     I can generate direct download links for any file you send me.

     🔹 **How to use:** Just send or forward a file here.
     🔹 **Commands:** /help, /status, /about
     🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**
```

#### 2. Uploading Files

Simply send any file to the bot:

**Supported File Types:**
- 📄 **Documents**: PDF, DOC, ZIP, RAR, APK, etc.
- 🎥 **Videos**: MP4, MKV, AVI, MOV, etc.
- 🎵 **Audio**: MP3, WAV, FLAC, M4A, etc.
- 🖼️ **Photos**: JPG, PNG, GIF, etc.

**Example Flow:**

```
You: [Sends video file: "movie.mp4" - 500MB]

Bot: 🔄 **Processing your file...**

Bot: ✅ **Link Generated!**

     📂 **Filename:** `movie.mp4`
     🔗 **Direct Link:**
     https://your-service.onrender.com/dl/12345

     ⚡ *Direct high-speed download enabled.*
     🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**
```

#### 3. Sharing Download Links

The generated link can be:
- Shared with anyone (no Telegram account needed)
- Downloaded directly in browser
- Streamed (for videos)
- Downloaded multiple times (permanent link)

**Link Format:**
```
https://your-service.onrender.com/dl/{message_id}
```

#### 4. Checking Bot Status

Send `/status` to check if bot is online:

```
You: /status

Bot: 📊 **System Status**

     ✅ **Bot:** Online
     ⏳ **Uptime:** `2d 5h 30m 15s`
     📡 **Mode:** Hybrid Polling (24/7)
     📂 **Log Channel:** `-1001234567890`
     🌐 **Server:** Render Cloud
     🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**
```

### File Size Limits

| Account Type | Maximum File Size |
|--------------|-------------------|
| Regular Telegram Users | 2 GB |
| Telegram Premium Users | 4 GB |

**Note**: File size limit is determined by your Telegram account type, not the bot.

### Link Behavior

**✅ Links Are Permanent If:**
- File stays in log channel
- Channel is not deleted
- Bot remains admin in channel

**❌ Links Break If:**
- File deleted from log channel
- Bot removed from channel
- Channel deleted

### Privacy & Security

- **Bot only works in private chats** - For your security
- **Files stored in YOUR channel** - You control the data
- **Private channel required** - Files not publicly accessible
- **Links are private** - Only people you share with can access
- **No file scanning** - Bot doesn't analyze file contents

## 🔧 How It Works

1. **User uploads a file** to the bot via Telegram
2. **Bot uses HTTP polling** to receive updates from Telegram API
3. **Bot forwards the file** to your private log channel for permanent storage
4. **Bot generates a unique link** using the message ID from the log channel
5. **Web server streams the file** when someone accesses the link
6. **Direct download** happens via chunk-by-chunk streaming from Telegram

### Architecture

```
User → Telegram → Bot (HTTP Polling) → Log Channel (Storage)
                         ↓
User → Download Link → Web Server → Telegram API → File Stream
                         ↓
                   Keep-Alive Task (24/7 Uptime)
```

### Technical Details

- Uses **HTTP polling** (via Telegram's getUpdates API) for receiving updates instead of webhooks
- Implements **24/7 keep-alive mechanism** that pings itself every 10 minutes
- Streams files **chunk-by-chunk** to minimize memory usage
- Runs **three concurrent tasks**: Pyrogram client, HTTP polling, and keep-alive pinger
- **Hybrid polling system** processes commands and media in real-time

## 📖 Complete Code Explanation

### Main Components Overview

The bot consists of three main components that run concurrently:

1. **Pyrogram Client** - Handles Telegram API interactions
2. **HTTP Polling System** - Receives and processes user messages
3. **Aiohttp Web Server** - Serves files via direct download links
4. **Keep-Alive System** - Maintains 24/7 uptime on free hosting

### Code Structure Breakdown

#### 1. Configuration and Setup (Lines 1-44)

```python
import os
import asyncio
import logging
import aiohttp
import time
import json
import urllib.request
from datetime import datetime
from pyrogram import Client
from aiohttp import web
```

**Imports Explanation:**
- `os`: Access environment variables for configuration
- `asyncio`: Enable asynchronous programming for concurrent operations
- `logging`: Debug and monitor bot activities
- `aiohttp`: Create HTTP server and client for file streaming
- `time`: Track timing for keep-alive pings
- `json`: Parse Telegram API responses
- `datetime`: Calculate bot uptime
- `pyrogram.Client`: Interact with Telegram's MTProto API
- `aiohttp.web`: Build web server for file downloads

```python
# Configuration variables
API_ID = int(os.environ.get("API_ID", 0)) 
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL_RAW = os.environ.get("LOG_CHANNEL", "")
PORT = int(os.environ.get("PORT", 8080))
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
```

**Environment Variables:**
- `API_ID`: Telegram API ID from my.telegram.org (integer)
- `API_HASH`: Telegram API hash for authentication (string)
- `BOT_TOKEN`: Bot token from @BotFather for bot authentication
- `LOG_CHANNEL`: Channel ID or username where files are stored (required, no default)
- `PORT`: HTTP server port (default: 8080)
- `APP_URL`: External URL for generating download links and self-ping

```python
START_TIME = datetime.now()  # Track when bot started for uptime calculation
```

```python
# Sanitize Channel ID / Username
try:
    if LOG_CHANNEL_RAW.startswith("-") or LOG_CHANNEL_RAW.isdigit():
        LOG_CHANNEL = int(LOG_CHANNEL_RAW)  # Numeric channel ID
    else:
        LOG_CHANNEL = LOG_CHANNEL_RAW  # Username (e.g., @channelname)
except ValueError:
    LOG_CHANNEL = LOG_CHANNEL_RAW
```

**Channel ID Processing:**
- Detects if channel identifier is numeric (e.g., `-1001234567890`)
- Converts numeric IDs to integers for API calls
- Keeps usernames as strings (e.g., `@channelname`)
- Handles conversion errors gracefully

```python
# Pyrogram Client Configuration
app = Client(
    "file_to_link_bot",       # Session name
    api_id=API_ID,            # Your API ID
    api_hash=API_HASH,        # Your API hash
    bot_token=BOT_TOKEN,      # Bot token
    in_memory=True,           # Store session in RAM (no session file)
    ipv6=False                # Disable IPv6 for compatibility
)
```

**Client Configuration:**
- `in_memory=True`: No session files created, faster restarts
- `ipv6=False`: Better compatibility with various hosting services
- Session stored in memory for stateless deployments

#### 2. Helper Functions (Lines 48-63)

```python
def get_uptime():
    """Calculate bot uptime in human-readable format"""
    delta = datetime.now() - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m {seconds}s"
```

**Uptime Calculation:**
- Calculates time difference since bot started
- Converts seconds to days, hours, minutes, seconds
- Returns formatted string (e.g., "2d 5h 30m 15s")
- Used in `/status` command to show bot reliability

```python
def get_filename(msg_obj):
    """Extract filename from Telegram message object"""
    # For Pyrogram copy_message results
    if hasattr(msg_obj, 'document') and msg_obj.document:
        return msg_obj.document.file_name or "file.bin"
    if hasattr(msg_obj, 'video') and msg_obj.video:
        return msg_obj.video.file_name or "video.mp4"
    if hasattr(msg_obj, 'audio') and msg_obj.audio:
        return msg_obj.audio.file_name or "audio.mp3"
    return "file"
```

**Filename Extraction:**
- Checks message for different media types (document, video, audio)
- Extracts original filename from media attributes
- Provides default filenames if original name is missing
- Handles various media types with fallback defaults

#### 3. Keep-Alive System (Lines 66-79)

```python
async def keep_alive():
    """
    24/7 Keep-Alive System
    - Prevents free hosting services from sleeping the app
    - Pings itself every 10 minutes
    - Essential for Render.com free tier
    """
    if not APP_URL:
        print("--- ⚠️ No APP_URL found. Self-ping disabled. ---")
        return
    
    print(f"--- ⏰ Starting 24/7 Keep-Alive for {APP_URL} ---")
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(APP_URL, timeout=10) as resp:
                    print(f"--- 💤 Ping Status: {resp.status} at {time.ctime()} ---")
            except Exception as e:
                print(f"--- 💤 Ping Error: {e} ---")
            await asyncio.sleep(600)  # 10 minutes = 600 seconds
```

**How It Works:**
1. **Purpose**: Keeps the bot alive on free hosting that sleeps after inactivity
2. **Mechanism**: Self-pings every 10 minutes (600 seconds)
3. **Process**:
   - Creates persistent HTTP client session
   - Sends GET request to bot's own health endpoint
   - Logs response status and timestamp
   - Handles network errors gracefully
   - Repeats indefinitely in background
4. **Why 10 Minutes**: Free hosting typically sleeps after 15-30 minutes of inactivity

#### 4. Hybrid Polling System (Lines 82-180)

```python
async def start_polling():
    """
    Custom HTTP Polling System
    - Alternative to webhooks (better for free hosting)
    - Receives updates directly from Telegram
    - Processes commands and media files
    - Runs 24/7 with automatic error recovery
    """
    print("--- 🚀 Starting Hybrid Update Poller ---")
    offset = 0  # Track last processed update
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
```

**Polling vs Webhooks:**
- **Polling**: Bot asks Telegram "any new messages?" repeatedly
- **Webhooks**: Telegram pushes messages to your server
- **Why Polling Here**: Works on free hosting without SSL certificate
- **Offset**: Ensures each update is processed only once

```python
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Long polling: wait up to 20 seconds for new updates
                async with session.get(base_url, params={"offset": offset, "timeout": 20}) as resp:
                    data = await resp.json()
                
                if not data.get("ok"):
                    await asyncio.sleep(5)
                    continue
```

**Long Polling:**
- `timeout=20`: Telegram holds connection for 20 seconds waiting for updates
- More efficient than repeatedly asking immediately
- Reduces unnecessary API calls
- If no updates, connection closes after 20 seconds and reopens

```python
                for update in data.get("result", []):
                    offset = update["update_id"] + 1  # Mark as processed
                    if "message" not in update: continue
                    
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    msg_id = msg["message_id"]
                    text = msg.get("text", "")
```

**Update Processing:**
- Each update has unique `update_id`
- `offset = update_id + 1` prevents reprocessing same update
- Extracts message data: chat ID, message ID, text content
- Skips non-message updates (e.g., inline queries)

**Command Handlers:**

```python
                    # /start command
                    if text.startswith("/start"):
                        welcome_text = (
                            "👋 **Welcome to FileToLink Bot!**\n\n"
                            "I can generate direct download links for any file you send me.\n\n"
                            "🔹 **How to use:** Just send or forward a file here.\n"
                            "🔹 **Commands:** /help, /status, /about"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        await app.send_message(chat_id, welcome_text)
                        continue
```

**Command Flow:**
1. User sends `/start`
2. Bot detects text starts with `/start`
3. Sends welcome message using Pyrogram
4. `continue` skips to next update

```python
                    # /status command
                    if text.startswith("/status"):
                        status_text = (
                            "📊 **System Status**\n\n"
                            f"✅ **Bot:** Online\n"
                            f"⏳ **Uptime:** `{get_uptime()}`\n"
                            f"📡 **Mode:** Hybrid Polling (24/7)\n"
                            f"📂 **Log Channel:** `{LOG_CHANNEL_RAW}`\n"
                            f"🌐 **Server:** Render Cloud"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        await app.send_message(chat_id, status_text)
                        continue
```

**Status Command:**
- Shows real-time bot statistics
- Displays uptime using `get_uptime()` function
- Confirms bot is running and operational
- Useful for monitoring and debugging

**Media Handling:**

```python
                    # Check for media keys (document, video, audio, photo)
                    has_media = any(k in msg for k in ["document", "video", "audio", "photo"])
                    if not has_media:
                        if text and not text.startswith("/"):
                            await app.send_message(chat_id, "❌ **Please send a valid file.**\nUse /help for more info.")
                        continue
```

**Media Detection:**
- Checks if message contains any media type
- `any()` returns True if at least one media key exists
- Rejects text-only messages (except commands)
- User-friendly error message for invalid input

```python
                    status = await app.send_message(chat_id, "🔄 **Processing your file...**")
                    try:
                        # Copy message to Log Channel
                        log_msg = await app.copy_message(LOG_CHANNEL, chat_id, msg_id)
```

**File Processing Steps:**

1. **Send Status**: Inform user that processing started
2. **Copy to Channel**: 
   - `copy_message()` duplicates file to log channel
   - Preserves file without re-uploading
   - Faster than download + upload
   - Returns message object with new message ID

```python
                        file_url = f"{APP_URL}/dl/{log_msg.id}"
                        filename = get_filename(log_msg)
```

3. **Generate Link**:
   - Uses message ID from log channel: `log_msg.id`
   - Creates URL pattern: `https://your-app.com/dl/12345`
   - Web server will use this ID to fetch and stream the file

```python
                        success_text = (
                            "✅ **Link Generated!**\n\n"
                            f"📂 **Filename:** `{filename}`\n"
                            f"🔗 **Direct Link:**\n{file_url}\n\n"
                            "⚡ *Direct high-speed download enabled.*"
                            " 🧑🏻‍💻 **Developer:** @WhiteDeathGaming **WDG**"
                        )
                        
                        await app.edit_message_text(chat_id, status.id, success_text)
```

4. **Send Result**:
   - Edits "Processing..." message to show success
   - Includes filename and download link
   - User can now share this link with anyone

```python
                    except Exception as e:
                        print(f"Processing Error: {e}")
                        await app.edit_message_text(chat_id, status.id, f"❌ **Error:** {e}\n\nPlease check if the bot is an admin in the log channel.")
```

5. **Error Handling**:
   - Catches any processing errors
   - Logs error to console for debugging
   - Shows user-friendly error message
   - Common issue: Bot not admin in log channel

#### 5. Web Server & File Streaming (Lines 183-204)

```python
async def handle_stream(request):
    """
    HTTP Request Handler for File Downloads
    - Receives requests to /dl/{message_id}
    - Fetches file from Telegram via message ID
    - Streams file directly to user's browser
    - Minimizes memory usage with chunk streaming
    """
    try:
        # Extract message ID from URL
        message_id = int(request.match_info['id'])
```

**URL Structure:**
- User visits: `https://your-app.com/dl/12345`
- `request.match_info['id']` extracts `12345`
- Converts to integer for Telegram API call

```python
        # Fetch message from log channel
        msg = await app.get_messages(LOG_CHANNEL, message_id)
        if not msg or not msg.media:
            return web.Response(status=404, text="Not Found")
```

**Message Retrieval:**
- `get_messages()` fetches specific message by ID
- Checks if message exists and contains media
- Returns 404 error if file not found or deleted

```python
        # Extract media object and metadata
        media = getattr(msg, msg.media.value)
        filename = getattr(media, "file_name", "file") or "file"
```

**Media Processing:**
- `msg.media.value` returns media type (e.g., "document")
- `getattr()` retrieves the media object
- Extracts filename with fallback to "file"

```python
        # Prepare streaming response with proper headers
        response = web.StreamResponse(status=200, headers={
            'Content-Type': getattr(media, "mime_type", "application/octet-stream"),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(media.file_size)
        })
```

**HTTP Headers Explanation:**
- `Content-Type`: Tells browser what type of file it is (video/mp4, etc.)
- `Content-Disposition`: Forces download with original filename
- `Content-Length`: Total file size for download progress bar

```python
        await response.prepare(request)
        async for chunk in app.stream_media(msg):
            await response.write(chunk)
        return response
```

**Chunk Streaming:**
1. `response.prepare()`: Opens connection to client
2. `stream_media()`: Gets file from Telegram in chunks (typically 256KB)
3. `response.write(chunk)`: Sends each chunk to client immediately
4. **Benefits**:
   - Low memory usage (only one chunk in RAM at a time)
   - Large files (2GB+) can be streamed without loading fully
   - Faster start (user sees download progress immediately)

```python
    except Exception as e:
        return web.Response(status=500, text=str(e))
```

**Error Handling:**
- Catches any streaming errors
- Returns 500 error with error message
- Prevents server crash on individual request failure

```python
async def health_check(request):
    """
    Health Check Endpoint
    - Responds to keep-alive pings
    - Shows bot is running
    - Displays current uptime
    """
    return web.Response(text=f"Bot is running 24/7\nUptime: {get_uptime()}")
```

**Health Check Purpose:**
- Root endpoint `/` returns simple status
- Used by keep-alive system to ping itself
- Can be used by external monitoring services
- Quick way to verify bot is running

#### 6. Startup & Orchestration (Lines 206-241)

```python
async def start_services():
    """
    Main Startup Function
    - Initializes Pyrogram client
    - Resolves log channel
    - Starts web server
    - Launches concurrent tasks
    """
    print("--- 🤖 Starting Telegram Client ---")
    await app.start()
```

**Client Initialization:**
- `app.start()`: Connects to Telegram servers
- Authenticates with API credentials
- Creates session for all API calls
- Must be called before any Telegram operations

```python
    # Resolve channel on startup
    resolved = False
    for i in range(3):
        try:
            print(f"--- 🔎 Attempting to resolve Log Channel: {LOG_CHANNEL} ---")
            chat = await app.get_chat(LOG_CHANNEL)
            print(f"--- ✅ Log Channel Resolved: {chat.title} ---")
            resolved = True
            break
        except Exception as e:
            print(f"--- ⚠️ Resolution attempt {i+1} failed: {e} ---")
            await asyncio.sleep(3)
```

**Channel Resolution:**
- **Why Important**: Bot must "know" the channel before interacting
- **3 Attempts**: Retries if first attempt fails (network issues, etc.)
- **get_chat()**: Fetches channel info and registers it in session
- **3-Second Delay**: Waits between retries to avoid rate limits
- **Common Failure**: Channel ID wrong or bot not added as admin

```python
    # Configure web server
    server = web.Application()
    server.router.add_get('/dl/{id}', handle_stream)  # File download endpoint
    server.router.add_get('/', health_check)          # Health check endpoint
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', PORT).start()
```

**Web Server Setup:**
- `web.Application()`: Creates aiohttp web app
- **Routes**:
  - `/dl/{id}`: Dynamic route for file downloads (e.g., `/dl/12345`)
  - `/`: Root endpoint for health checks
- `0.0.0.0`: Listen on all network interfaces
- `PORT`: Configurable port (default 8080)

```python
    print(f"--- 🌐 Web Server running on port {PORT} ---")
    
    # Run all tasks concurrently
    await asyncio.gather(
        keep_alive(),      # Task 1: Self-ping every 10 minutes
        start_polling()    # Task 2: Poll Telegram for updates
    )
```

**Concurrent Task Execution:**
- `asyncio.gather()`: Runs multiple async functions simultaneously
- **Task 1 (keep_alive)**: Pings itself every 10 minutes for 24/7 uptime
- **Task 2 (start_polling)**: Continuously polls Telegram for user messages
- **Task 3 (implicit)**: Web server runs in background serving requests
- All three run in parallel using Python's async/await

```python
if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except (KeyboardInterrupt, SystemExit):
        pass
```

**Application Entry Point:**
- `if __name__ == "__main__"`: Only runs when script executed directly
- `asyncio.run()`: Starts async event loop and runs main function
- **Error Handling**: 
  - Catches Ctrl+C (KeyboardInterrupt) for graceful shutdown
  - Catches system exit signals
  - `pass`: Exits silently without error message

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION STARTUP                       │
│  1. Load environment variables                              │
│  2. Initialize Pyrogram client                              │
│  3. Resolve log channel                                     │
│  4. Start web server on PORT                                │
│  5. Launch concurrent tasks                                 │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌─────────────┐ ┌──────────────┐ ┌───────────────┐
    │ Keep-Alive  │ │   Polling    │ │  Web Server   │
    │   System    │ │    System    │ │   (aiohttp)   │
    └─────────────┘ └──────────────┘ └───────────────┘
            │               │               │
            ▼               ▼               ▼
    Every 10 min:    Telegram API:    HTTP Requests:
    - Ping self      - getUpdates     - /dl/{id}
    - Keep alive     - Process msgs   - Stream files
                     - Handle cmds    - /health check
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌────────────┐  ┌─────────────┐  ┌──────────────┐
    │  Commands  │  │ File Upload │  │ File Download│
    │ /start     │  │  1. Detect  │  │ 1. Get msg ID│
    │ /help      │  │  2. Copy    │  │ 2. Fetch file│
    │ /status    │  │  3. Generate│  │ 3. Stream    │
    │ /about     │  │  4. Reply   │  │ 4. Download  │
    └────────────┘  └─────────────┘  └──────────────┘
```

### Key Design Decisions

1. **Why Polling Instead of Webhooks?**
   - Free hosting often lacks SSL certificates
   - Webhooks require HTTPS
   - Polling works on any hosting platform
   - Long polling reduces API calls

2. **Why Store Files in Telegram Channel?**
   - Telegram provides free unlimited storage
   - Files remain available as long as channel exists
   - No need for separate file storage service
   - Direct streaming from Telegram's CDN

3. **Why Three Concurrent Tasks?**
   - **Keep-Alive**: Prevents free hosting from sleeping
   - **Polling**: Receives and processes user messages
   - **Web Server**: Serves download requests
   - All must run simultaneously for 24/7 operation

4. **Why Chunk Streaming?**
   - Memory efficient (only one chunk in RAM)
   - Supports large files (2GB+) without timeout
   - Faster user experience (download starts immediately)
   - No disk I/O (streams directly from Telegram to user)

5. **Why In-Memory Session?**
   - `in_memory=True` avoids session file creation
   - Suitable for stateless container deployments
   - Faster restarts on platforms like Render
   - No persistent storage needed

## 📁 Project Structure

```
File_To_Link/
├── main.py                 # Main application file (242 lines)
│   ├── Configuration       # Environment variables & setup (lines 1-44)
│   ├── Helper Functions    # Utility functions (lines 48-63)
│   ├── Keep-Alive System   # 24/7 uptime mechanism (lines 66-79)
│   ├── Polling System      # Message processing (lines 82-180)
│   ├── Web Server          # File streaming server (lines 183-203)
│   └── Startup Logic       # Application initialization (lines 206-241)
│
├── requirements.txt        # Python dependencies
│   ├── pyrogram==2.0.106   # Telegram API framework
│   ├── tgcrypto==1.2.5     # Cryptographic acceleration
│   └── aiohttp==3.9.1      # Async HTTP server/client
│
├── Procfile                # Deployment configuration for Render
│   └── web: python main.py # Command to start the bot
│
└── README.md               # This documentation file
```

### File Descriptions

#### main.py
The core application file containing all bot logic:

**Imports & Configuration (Lines 1-44)**
- Loads required libraries
- Reads environment variables
- Initializes Pyrogram client
- Configures logging

**Helper Functions (Lines 48-63)**
- `get_uptime()`: Calculates bot uptime
- `get_filename()`: Extracts filename from media

**Keep-Alive System (Lines 66-79)**
- `keep_alive()`: Pings itself every 10 minutes
- Prevents free hosting from sleeping
- Essential for 24/7 operation

**Polling System (Lines 82-180)**
- `start_polling()`: Main message handler
- Processes commands (/start, /help, /status, /about)
- Handles file uploads
- Generates download links

**Web Server (Lines 183-203)**
- `handle_stream()`: Streams files to users
- `health_check()`: Uptime monitoring endpoint
- Serves files via HTTP

**Startup Logic (Lines 206-241)**
- `start_services()`: Initializes everything
- Resolves log channel
- Starts web server
- Launches concurrent tasks

#### requirements.txt
Python package dependencies:

```txt
pyrogram==2.0.106    # Telegram MTProto API framework
tgcrypto==1.2.5      # Fast cryptography for Pyrogram
aiohttp==3.9.1       # Async HTTP server and client
```

**Why These Packages:**
- **pyrogram**: Modern, async Telegram framework with clean API
- **tgcrypto**: Speeds up Telegram encryption (10-100x faster)
- **aiohttp**: Async web server for streaming files

#### Procfile
Tells hosting platforms how to run the app:

```
web: python main.py
```

- `web`: Process type (web service)
- `python main.py`: Command to start the bot

## ⚙️ Configuration Guide

### Environment Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `API_ID` | Integer | ✅ Yes | `0` | Telegram API ID from my.telegram.org |
| `API_HASH` | String | ✅ Yes | `""` | Telegram API Hash from my.telegram.org |
| `BOT_TOKEN` | String | ✅ Yes | `""` | Bot token from @BotFather |
| `LOG_CHANNEL` | String/Int | ✅ Yes | None (required) | Channel ID or username for file storage |
| `PORT` | Integer | ⚠️ Auto | `8080` | HTTP server port (set by hosting) |
| `RENDER_EXTERNAL_URL` | String | ✅ Yes | `""` | Public URL for generating download links |

### Configuration Examples

**Local Development:**
```bash
# Linux/Mac
export API_ID="12345678"
export API_HASH="your_api_hash_here"
export BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export LOG_CHANNEL="-1001234567890"
export PORT="8080"
export RENDER_EXTERNAL_URL="http://localhost:8080"

# Windows
set API_ID=12345678
set API_HASH=your_api_hash_here
set BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
set LOG_CHANNEL=-1001234567890
set PORT=8080
set RENDER_EXTERNAL_URL=http://localhost:8080
```

**Production (Render):**
Set in Render dashboard → Environment tab:
```
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
LOG_CHANNEL=-1001234567890
PORT=8080
RENDER_EXTERNAL_URL=https://your-service.onrender.com
```

### Variable Details

#### API_ID & API_HASH
- **Purpose**: Authenticate with Telegram's MTProto API
- **Source**: [my.telegram.org](https://my.telegram.org) → API Development Tools
- **Format**: 
  - API_ID: Integer (e.g., `12345678`)
  - API_HASH: String (e.g., `0123456789abcdef0123456789abcdef`)
- **Security**: Keep secret, never commit to Git

#### BOT_TOKEN
- **Purpose**: Authenticate your bot
- **Source**: [@BotFather](https://t.me/BotFather) → `/newbot`
- **Format**: `{bot_id}:{secret_token}` (e.g., `123456789:ABCdefGHI...`)
- **Security**: Anyone with this can control your bot

#### LOG_CHANNEL
- **Purpose**: Storage location for uploaded files
- **Formats**: 
  - Channel ID: `-1001234567890` (recommended)
  - Username: `@channelname` (must be public)
- **Requirements**:
  - Bot must be admin in channel
  - Channel should be private for security
  - Grant "Post Messages" permission to bot

#### PORT
- **Purpose**: HTTP server port
- **Default**: `8080`
- **Note**: Render sets this automatically, don't override

#### RENDER_EXTERNAL_URL
- **Purpose**: Generate correct download links
- **Format**: Full URL with protocol (e.g., `https://your-app.onrender.com`)
- **Important**: Must match your actual service URL
- **Usage**: Appended with `/dl/{message_id}` for file links

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ **DO**: Use environment variables for all secrets
- ✅ **DO**: Set variables in hosting platform dashboard
- ❌ **DON'T**: Hardcode secrets in code
- ❌ **DON'T**: Commit `.env` files to Git

### 2. Channel Security
- ✅ **DO**: Use private channels for storage
- ✅ **DO**: Only add bot as admin (minimize access)
- ❌ **DON'T**: Use public channels (anyone can access files)
- ❌ **DON'T**: Share channel ID publicly

### 3. Bot Token
- ✅ **DO**: Generate new token if compromised
- ✅ **DO**: Revoke token when not in use
- ❌ **DON'T**: Share bot token with anyone
- ❌ **DON'T**: Post token in forums/chat groups

### 4. File Sharing
- ✅ **DO**: Only share links with intended recipients
- ✅ **DO**: Delete files from channel when no longer needed
- ❌ **DON'T**: Share download links publicly
- ❌ **DON'T**: Upload sensitive/personal data

### 5. Code Security
- ✅ **DO**: Review code before deployment
- ✅ **DO**: Keep dependencies updated
- ❌ **DON'T**: Install untrusted packages
- ❌ **DON'T**: Modify code without understanding it

### Git Security Checklist

Before committing code:

```bash
# Check for accidental secrets
git diff

# Verify .gitignore excludes sensitive files
cat .gitignore

# Recommended .gitignore entries:
# .env
# *.session
# config.py
# __pycache__/
# *.pyc
```

### If You Leak Secrets

**Bot Token Leaked:**
1. Go to @BotFather
2. Send `/mybots`
3. Select your bot
4. Click "API Token" → "Revoke current token"
5. Get new token
6. Update in environment variables

**API Credentials Leaked:**
1. Go to my.telegram.org
2. Delete compromised application
3. Create new application
4. Get new API_ID and API_HASH
5. Update in environment variables

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Bot Not Responding

**Symptoms:**
- Bot doesn't reply to `/start` or other commands
- No response when sending files

**Possible Causes & Solutions:**

**a) Invalid Bot Token**
```bash
# Check if token format is correct
# Format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Verify token with Telegram API
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

# If returns error, token is invalid - get new one from @BotFather
```

**b) Environment Variables Not Set**
```bash
# Check if variables are set (Linux/Mac)
echo $API_ID
echo $API_HASH
echo $BOT_TOKEN

# For Windows
echo %API_ID%

# If empty, set them again
```

**c) Bot Process Not Running**
```bash
# Check logs in Render dashboard
# Look for errors like:
# - "Connection refused"
# - "Invalid token"
# - "API_ID not set"

# Restart service in Render dashboard
```

#### 2. PEER_ID_INVALID Error

**Symptoms:**
```
Processing Error: [400 PEER_ID_INVALID]
Please check if the bot is an admin in the log channel.
```

**Why This Happens:**
- Bot hasn't "met" the channel yet
- Bot needs to interact with channel before copying messages

**Solutions (Try in order):**

**Solution 1: Forward Message to Bot**
1. Open your private channel
2. Forward any message from channel to your bot
3. Bot now "knows" the channel
4. Try uploading file again

**Solution 2: Send Message in Channel**
1. Open your private channel
2. Send any message (e.g., "test")
3. Wait 30 seconds
4. Try uploading file again

**Solution 3: Remove and Re-add Bot**
1. Remove bot from channel administrators
2. Wait 1 minute
3. Add bot back as administrator
4. Grant "Post Messages" permission
5. Forward message from channel to bot
6. Try uploading file again

**Solution 4: Use Correct Channel ID**
```bash
# Verify channel ID format:
# ✅ Correct: -1001234567890 (with minus sign)
# ❌ Wrong: 1001234567890 (missing minus)
# ❌ Wrong: -100123456789 (missing digit)

# Get channel ID using @userinfobot:
# 1. Forward message from channel to @userinfobot
# 2. Copy the ID it returns
# 3. Update LOG_CHANNEL environment variable
```

#### 3. Download Links Not Working

**Symptoms:**
- Clicking link shows "Not Found" (404 error)
- Link doesn't download file
- Browser shows connection error

**Solutions:**

**a) Check RENDER_EXTERNAL_URL**
```bash
# Verify URL is set correctly
# Should match your Render service URL exactly

# ✅ Correct format:
https://your-service.onrender.com

# ❌ Wrong formats:
http://your-service.onrender.com  (missing 's' in https)
https://your-service.onrender.com/  (extra slash)
your-service.onrender.com  (missing https://)
```

**b) Verify Web Server is Running**
```bash
# Test health endpoint
curl https://your-service.onrender.com/

# Should return:
# "Bot is running 24/7
# Uptime: Xd Xh Xm Xs"

# If error, check Render logs for web server issues
```

**c) Check Message ID Exists**
```bash
# If link is: https://your-app.com/dl/12345
# Message ID is: 12345

# Possible issues:
# - Message deleted from channel
# - Wrong channel ID in LOG_CHANNEL
# - Message doesn't contain media
```

**d) Verify File Still in Channel**
1. Open your log channel
2. Find message with ID from link
3. If deleted, file is gone (regenerate link)

#### 4. File Upload Errors

**Symptoms:**
- Bot says "Processing..." but never completes
- "Error: File too large"
- Upload timeout

**Solutions:**

**a) Check File Size**
```
Maximum file sizes:
- Regular users: 2 GB
- Premium users: 4 GB

Solution: Split large files or upgrade to Premium
```

**b) Bot Not Admin in Channel**
```bash
# Verify bot has correct permissions:
# 1. Open channel
# 2. Channel info → Administrators
# 3. Find your bot
# 4. Check these permissions:
#    ✅ Post Messages (REQUIRED)
#    ✅ Edit Messages (optional)
#    ✅ Delete Messages (optional)
```

**c) Network Timeout**
```bash
# Large files may timeout on slow connections
# Render free tier may have timeouts

# Solution:
# - Try smaller file first (test with <10MB)
# - If small file works, issue is network/timeout
# - Consider upgrading hosting plan
```

#### 5. Bot Keeps Going Offline

**Symptoms:**
- Bot responds, then stops after 15-30 minutes
- Render shows "Service is sleeping"

**Solutions:**

**a) Verify Keep-Alive is Running**
```bash
# Check logs for:
--- ⏰ Starting 24/7 Keep-Alive for https://your-app.com ---
--- 💤 Ping Status: 200 at {timestamp} ---

# Should see ping every 10 minutes
```

**b) Set Up External Monitoring**
```bash
# Use UptimeRobot (recommended):
# 1. Go to uptimerobot.com
# 2. Add monitor for your service URL
# 3. Set interval to 5 minutes
# 4. UptimeRobot will ping your bot

# Use Cron-Job.org (alternative):
# 1. Go to cron-job.org
# 2. Create job for your URL
# 3. Set to every 10 minutes
```

**c) Check Render Plan Limits**
```bash
# Free tier limitations:
# - 750 hours/month (about 31 days)
# - May sleep after 15 min inactivity
# - Keep-alive should prevent sleeping

# If still sleeping, consider:
# - Paid plan ($7/month for always-on)
# - Different hosting (Railway, Heroku)
```

#### 6. "Cannot Import" or "Module Not Found" Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'pyrogram'
ImportError: cannot import name 'Client'
```

**Solutions:**

**a) Install Dependencies**
```bash
# Make sure requirements.txt exists
cat requirements.txt

# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install pyrogram==2.0.106
pip install tgcrypto==1.2.5
pip install aiohttp==3.9.1
```

**b) Check Python Version**
```bash
# Verify Python 3.7+
python --version

# If Python 2.x or < 3.7:
# - Install Python 3.7 or higher
# - Use python3 instead of python
python3 --version
python3 main.py
```

**c) Virtual Environment Issues**
```bash
# Create fresh virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 7. "Session File Already Exists" Error

**Symptoms:**
```
Error: Session file is already in use
```

**Solution:**
```bash
# The bot uses in_memory=True, so this shouldn't happen
# If it does, delete session file:

# Find session files
ls *.session

# Delete them
rm *.session

# Or delete specific file
rm file_to_link_bot.session

# Restart bot
python main.py
```

### Getting Help

If you still have issues:

1. **Check Logs First:**
   - Render: Dashboard → Logs tab
   - Local: Terminal output

2. **Search Existing Issues:**
   - [GitHub Issues](https://github.com/Tom2001moT/File_To_Link/issues)
   - Someone may have solved it already

3. **Create New Issue:**
   - Go to [GitHub Issues](https://github.com/Tom2001moT/File_To_Link/issues/new)
   - Provide:
     - Clear description of problem
     - Error messages from logs
     - Steps to reproduce
     - Environment (OS, Python version, hosting)
   - **Don't include secrets** (API_ID, tokens, etc.)

4. **Debug Mode:**
   ```python
   # Add to top of main.py for more detailed logs
   logging.basicConfig(level=logging.DEBUG)
   ```

### Error Log Examples

**Successful Startup:**
```
--- 🤖 Starting Telegram Client ---
--- 🔎 Attempting to resolve Log Channel: -1001234567890 ---
--- ✅ Log Channel Resolved: My Channel ---
--- 🌐 Web Server running on port 8080 ---
--- ⏰ Starting 24/7 Keep-Alive for https://app.onrender.com ---
--- 🚀 Starting Hybrid Update Poller ---
--- 💤 Ping Status: 200 at Fri Dec 27 15:00:00 2024 ---
```

**Configuration Error:**
```
--- 🤖 Starting Telegram Client ---
ERROR: API_ID not set or invalid
Traceback (most recent call last):
  File "main.py", line 237, in <module>
    asyncio.run(start_services())

# Solution: Set API_ID environment variable
```

**Channel Resolution Error:**
```
--- 🔎 Attempting to resolve Log Channel: -1001234567890 ---
--- ⚠️ Resolution attempt 1 failed: [400 CHAT_INVALID] ---
--- ⚠️ Resolution attempt 2 failed: [400 CHAT_INVALID] ---
--- ⚠️ Resolution attempt 3 failed: [400 CHAT_INVALID] ---

# Solution: Verify channel ID, add bot as admin
```

## 🚀 Advanced Features & Customization

### Customizing Bot Messages

You can modify bot responses by editing `main.py`:

**Location of Messages:**
- Welcome message: Line 109-116
- Help text: Line 120-128
- Status display: Line 132-141
- Success message: Line 165-171

**Example Customization:**

```python
# Change welcome message (Line 109-116)
welcome_text = (
    "🎉 **Welcome to MY Custom Bot!**\n\n"
    "Send files, get links!\n\n"
    "Commands: /help"
)

# Change success message (Line 165-171)
success_text = (
    "✅ **Done!**\n\n"
    f"📁 File: {filename}\n"
    f"🔗 Link: {file_url}"
)
```

### Adding Custom Commands

Add new commands in the polling function (around line 145):

```python
if text.startswith("/mycommand"):
    await app.send_message(chat_id, "This is my custom command!")
    continue
```

### Changing Keep-Alive Interval

Default: 10 minutes (600 seconds)

```python
# Line 79 in main.py
await asyncio.sleep(600)  # Change to desired seconds

# Examples:
await asyncio.sleep(300)   # 5 minutes
await asyncio.sleep(900)   # 15 minutes
await asyncio.sleep(1200)  # 20 minutes
```

**Note**: Shorter intervals = more frequent pings = better uptime but more resource usage

### Adding Download Statistics

Track downloads by modifying `handle_stream()`:

```python
# Add after line 184
download_count = {}  # Store at module level

async def handle_stream(request):
    message_id = int(request.match_info['id'])
    
    # Increment download counter
    download_count[message_id] = download_count.get(message_id, 0) + 1
    
    # Log download
    logger.info(f"Download #{download_count[message_id]} for message {message_id}")
    
    # ... rest of function
```

### Multiple Bot Instances

Run multiple bots with different configs:

```bash
# Bot 1 - Personal files
export API_ID="12345678"
export BOT_TOKEN="bot1_token"
export LOG_CHANNEL="-1001111111111"
export PORT="8080"
python main.py &

# Bot 2 - Work files
export API_ID="12345678"
export BOT_TOKEN="bot2_token"
export LOG_CHANNEL="-1002222222222"
export PORT="8081"
python main.py &
```

### Using with Nginx Reverse Proxy

For production with custom domain:

```nginx
# /etc/nginx/sites-available/filetolink
server {
    listen 80;
    server_name files.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # Important for large files
        proxy_buffering off;
        proxy_request_buffering off;
        client_max_body_size 0;
    }
}
```

## 📊 Performance & Limitations

### Performance Metrics

Based on testing with Render free tier:

| Metric | Value |
|--------|-------|
| **Startup Time** | 10-15 seconds |
| **Response Time** | < 1 second (commands) |
| **File Upload** | ~30 seconds (500MB file) |
| **Download Speed** | Limited by Telegram CDN |
| **Concurrent Users** | 10-50 (free tier) |
| **Memory Usage** | ~100MB (idle) |
| **CPU Usage** | < 5% (idle) |

### Platform Limitations

**Render Free Tier:**
- ✅ 750 hours/month (31 days with keep-alive)
- ✅ 512MB RAM
- ✅ 0.1 CPU
- ⚠️ May sleep after inactivity (mitigated by keep-alive)
- ⚠️ Cold starts (10-15 sec)

**Telegram API:**
- ✅ Unlimited storage in channels
- ✅ 2GB file size (4GB for Premium)
- ⚠️ Rate limits: ~30 messages/second
- ⚠️ API calls limited per account

### Scaling Considerations

**For Higher Traffic:**
1. **Upgrade Hosting**: Render paid plan ($7/month)
2. **Use Redis**: Cache message IDs for faster lookup
3. **Add Database**: Track downloads and analytics
4. **Load Balancer**: Multiple bot instances
5. **CDN**: Cache frequent downloads

**Optimization Tips:**
```python
# Add connection pooling
app = Client(
    "file_to_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    max_concurrent_transmissions=10  # Parallel downloads
)
```

## 🔄 Alternative Deployment Options

### Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your forked repository
5. Add environment variables
6. Railway auto-detects Python and installs dependencies
7. Copy service URL to `RENDER_EXTERNAL_URL`

**Railway Advantages:**
- Generous free tier ($5 credit/month)
- Faster cold starts
- Better uptime
- Built-in domain

### Deploy on Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set API_ID="12345678"
heroku config:set API_HASH="your_hash"
heroku config:set BOT_TOKEN="your_token"
heroku config:set LOG_CHANNEL="-1001234567890"
heroku config:set RENDER_EXTERNAL_URL="https://your-app-name.herokuapp.com"

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Deploy on VPS (Ubuntu)

```bash
# Connect to your VPS
ssh user@your-vps-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip -y

# Clone repository
git clone https://github.com/Tom2001moT/File_To_Link.git
cd File_To_Link

# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
nano ~/.bashrc

# Add these lines:
export API_ID="12345678"
export API_HASH="your_hash"
export BOT_TOKEN="your_token"
export LOG_CHANNEL="-1001234567890"
export PORT="8080"
export RENDER_EXTERNAL_URL="http://your-vps-ip:8080"

# Reload bashrc
source ~/.bashrc

# Run with systemd (persistent)
sudo nano /etc/systemd/system/filetolink.service

# Service file content:
[Unit]
Description=File To Link Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/File_To_Link
Environment="API_ID=12345678"
Environment="API_HASH=your_hash"
Environment="BOT_TOKEN=your_token"
Environment="LOG_CHANNEL=-1001234567890"
Environment="PORT=8080"
Environment="RENDER_EXTERNAL_URL=http://your-vps-ip:8080"
ExecStart=/usr/bin/python3 /home/your-username/File_To_Link/main.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable filetolink
sudo systemctl start filetolink

# Check status
sudo systemctl status filetolink

# View logs
sudo journalctl -u filetolink -f
```

### Deploy on Docker

```dockerfile
# Create Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV API_ID=""
ENV API_HASH=""
ENV BOT_TOKEN=""
ENV LOG_CHANNEL=""
ENV PORT="8080"
ENV RENDER_EXTERNAL_URL=""

EXPOSE 8080

CMD ["python", "main.py"]
```

```bash
# Build image
docker build -t filetolink .

# Run container
docker run -d \
  -e API_ID="12345678" \
  -e API_HASH="your_hash" \
  -e BOT_TOKEN="your_token" \
  -e LOG_CHANNEL="-1001234567890" \
  -e PORT="8080" \
  -e RENDER_EXTERNAL_URL="http://localhost:8080" \
  -p 8080:8080 \
  --name filetolink \
  filetolink

# View logs
docker logs -f filetolink
```

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn and create. Any contributions you make are **greatly appreciated**!

### How to Contribute

1. **Fork the Repository**
   ```bash
   # Click "Fork" button on GitHub
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/File_To_Link.git
   cd File_To_Link
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Make Your Changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test your changes thoroughly

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: Amazing new feature"
   ```

5. **Push to Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```

6. **Open Pull Request**
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Describe your changes
   - Submit for review

### Contribution Guidelines

**Code Style:**
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Keep functions small and focused

**Commit Messages:**
```bash
# Good commit messages:
git commit -m "Add: Download counter feature"
git commit -m "Fix: PEER_ID_INVALID error handling"
git commit -m "Update: README with deployment guide"

# Bad commit messages:
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

**Testing:**
- Test locally before pushing
- Verify bot works with your changes
- Check for errors in logs
- Test edge cases

**Documentation:**
- Update README if adding features
- Add code comments for complex logic
- Include examples in documentation

### Feature Requests

Have an idea? Open an issue with:
- Clear description of feature
- Use case / why it's useful
- Example implementation (if possible)

### Bug Reports

Found a bug? Open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Error messages / logs
- Environment details (OS, Python version)

## 📝 License

This project is licensed under the **MIT License** - see below for details.

```
MIT License

Copyright (c) 2024 Tom2001moT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### What This Means:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ No warranty provided
- ⚠️ Author not liable

## 👤 Author & Credits

**Created by:** Tom2001moT

**GitHub:** [@Tom2001moT](https://github.com/Tom2001moT)

**Repository:** [File_To_Link](https://github.com/Tom2001moT/File_To_Link)

### Built With

- [Pyrogram](https://docs.pyrogram.org/) - Telegram MTProto API framework
- [Aiohttp](https://docs.aiohttp.org/) - Async HTTP client/server
- [TgCrypto](https://github.com/pyrogram/tgcrypto) - Cryptography library
- [Python](https://www.python.org/) - Programming language

### Acknowledgments

- Telegram for their amazing Bot API
- Render for free hosting
- Open source community for inspiration
- All contributors to this project

## 🌟 Support the Project

If you found this project helpful, please consider:

- ⭐ **Star this repository** on GitHub
- 🐛 **Report bugs** you encounter
- 💡 **Suggest features** you'd like to see
- 🤝 **Contribute code** to improve the bot
- 📢 **Share** with others who might find it useful

### Show Your Support

```bash
# Star the repository
https://github.com/Tom2001moT/File_To_Link

# Follow the developer
https://github.com/Tom2001moT
```

## 📞 Contact & Support

### Get Help

1. **Documentation**: Read this README thoroughly
2. **Issues**: Check [existing issues](https://github.com/Tom2001moT/File_To_Link/issues)
3. **New Issue**: [Create new issue](https://github.com/Tom2001moT/File_To_Link/issues/new)

### Connect

- **GitHub**: [@Tom2001moT](https://github.com/Tom2001moT)
- **Telegram**: Check repository for updates
- **Issues**: [GitHub Issues](https://github.com/Tom2001moT/File_To_Link/issues)

### FAQ

**Q: Is this bot free to use?**
A: Yes, completely free and open source.

**Q: Can I use this for commercial purposes?**
A: Yes, MIT license allows commercial use.

**Q: Do I need coding knowledge?**
A: Basic knowledge helpful, but guide is beginner-friendly.

**Q: Is my data safe?**
A: Files stored in YOUR private channel, you control everything.

**Q: Can I customize the bot?**
A: Yes, it's open source - modify as you wish.

**Q: Does it work on Windows?**
A: Yes, works on Windows, Linux, and macOS.

**Q: How much does hosting cost?**
A: Render free tier is sufficient, or $7/month for paid.

**Q: Can I run multiple bots?**
A: Yes, just use different tokens and ports.

## 📚 Additional Resources

### Tutorials
- [Telegram Bot Tutorial](https://core.telegram.org/bots/tutorial)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [Pyrogram Documentation](https://docs.pyrogram.org/)

### Similar Projects
- [Telegraph-FiletoLink](https://github.com/eyaadh/Telegraph-FiletoLink)
- [TelegramFileStreamBot](https://github.com/EverythingSuckz/TG-FileStreamBot)

### Useful Tools
- [UptimeRobot](https://uptimerobot.com/) - Monitor uptime
- [BotFather](https://t.me/BotFather) - Create bots
- [UserInfoBot](https://t.me/userinfobot) - Get channel IDs

---

## 🎉 Thank You!

Thank you for using File To Link Bot! If you have any questions or feedback, feel free to open an issue on GitHub.

**Made with ❤️ by Tom2001moT**

---

<div align="center">

**⭐ Star this repository if you found it helpful! ⭐**

[Report Bug](https://github.com/Tom2001moT/File_To_Link/issues) · [Request Feature](https://github.com/Tom2001moT/File_To_Link/issues) · [Contribute](https://github.com/Tom2001moT/File_To_Link/pulls)

</div>

---

**Last Updated:** December 2024

**Version:** 1.0.0

**Status:** ✅ Active Development

**Note:** This bot is for educational and personal use. Make sure you comply with Telegram's [Terms of Service](https://telegram.org/tos) when using it. The author is not responsible for misuse of this software.