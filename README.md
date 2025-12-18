# File To Link Bot 🔗

A Telegram bot that converts files into direct download links. Send any file (video, audio, document, photo) to the bot and get an instant shareable download link!

## ✨ Features

- 📤 **Upload Any File**: Supports videos, audio files, documents, and photos
- 🔗 **Direct Download Links**: Generates instant shareable download links
- 💾 **Large File Support**: Handles files up to 2GB (4GB for Telegram Premium users)
- 🚀 **Efficient Streaming**: Uses chunk-by-chunk streaming to minimize RAM usage
- ⚡ **Fast & Reliable**: Built with async/await for optimal performance
- 🔒 **Secure Storage**: Files are stored in your private Telegram channel

## 🛠️ Tech Stack

- **Python 3.7+**
- **Pyrogram**: Modern Telegram Bot API framework
- **Aiohttp**: Asynchronous HTTP server
- **TgCrypto**: Cryptographic library for Telegram
- **Uvloop**: High-performance event loop

## 📋 Prerequisites

Before you begin, you'll need:

1. **Telegram Account** - To create a bot and API credentials
2. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/BotFather)
3. **API ID & API Hash** - Get them from [my.telegram.org](https://my.telegram.org)
4. **Private Channel** - Create a private channel to store files
5. **Render Account** (or any hosting platform) - For deploying the bot

## 🚀 Quick Start

### Step 1: Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Navigate to "API Development Tools"
4. Create a new application
5. Copy your `API_ID` and `API_HASH`

### Step 2: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the `BOT_TOKEN` provided

### Step 3: Create a Private Channel

1. Create a new private channel in Telegram
2. Add your bot as an administrator to the channel
3. Get the channel ID:
   - Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the channel ID (it will be negative, e.g., `-1001234567890`)

### Step 4: Local Installation

```bash
# Clone the repository
git clone https://github.com/Tom2001moT/File_To_Link.git
cd File_To_Link

# Install dependencies
pip install -r requirements.txt

# Set environment variables (Linux/Mac)
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export BOT_TOKEN="your_bot_token"
export LOG_CHANNEL="-1001234567890"
export PORT="8080"

# Run the bot
python main.py
```

## ☁️ Deployment on Render

### Step 1: Fork and Deploy

1. Fork this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: `file-to-link-bot` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### Step 2: Set Environment Variables

In your Render service dashboard, add these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Your Telegram API ID | `12345678` |
| `API_HASH` | Your Telegram API Hash | `abcdef1234567890abcdef1234567890` |
| `BOT_TOKEN` | Your bot token from BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `LOG_CHANNEL` | Your private channel ID | `-1001234567890` |
| `PORT` | Port number (auto-set by Render) | `8080` |

### Step 3: Set External URL

After deployment, Render will provide you with a URL like `https://your-service.onrender.com`. You need to set this as an environment variable:

| Variable | Value |
|----------|-------|
| `RENDER_EXTERNAL_URL` | `https://your-service.onrender.com` |

### Step 4: Keep the Service Alive

Render's free tier may sleep after inactivity. The bot includes a health check endpoint at `/` to help with uptime monitoring. You can use services like [UptimeRobot](https://uptimerobot.com/) to ping your service every 5 minutes.

## 📖 Usage

1. **Start the Bot**: Send `/start` to your bot
2. **Send a File**: Upload any video, audio, document, or photo
3. **Get the Link**: The bot will respond with a direct download link
4. **Share**: Share the link with anyone - they can download the file directly

### Example

```
User: [Sends a video file]
Bot: ✅ File Saved!

     📂 Name: `my_video.mp4`
     🔗 Download Link:
     https://your-service.onrender.com/dl/12345

     ⚠️ Note: This link streams directly from Telegram.
```

## 🔧 How It Works

1. **User uploads a file** to the bot via Telegram
2. **Bot forwards the file** to your private log channel for permanent storage
3. **Bot generates a unique link** using the message ID from the log channel
4. **Web server streams the file** when someone accesses the link
5. **Direct download** happens via chunk-by-chunk streaming from Telegram

### Architecture

```
User → Telegram Bot → Log Channel (Storage)
                     ↓
User → Download Link → Web Server → Telegram API → File Stream
```

## 📁 Project Structure

```
File_To_Link/
├── main.py              # Main application file (bot + web server)
├── requirements.txt     # Python dependencies
├── Procfile            # Deployment configuration for Render
└── README.md           # This file
```

## 🔒 Security Notes

- Keep your `API_ID`, `API_HASH`, and `BOT_TOKEN` secret
- Never commit environment variables to version control
- Make sure your log channel is private
- Only add your bot as an administrator to the log channel
- The bot only works in private chats for security

## ⚙️ Configuration

All configuration is done via environment variables:

```python
API_ID          # Telegram API ID (integer)
API_HASH        # Telegram API Hash (string)
BOT_TOKEN       # Bot token from BotFather (string)
LOG_CHANNEL     # Private channel ID for file storage (integer)
PORT            # Port for web server (default: 8080)
RENDER_EXTERNAL_URL  # Your service URL (for generating links)
```

## 🐛 Troubleshooting

### Bot Not Responding
- Check if environment variables are set correctly
- Verify bot token is valid
- Ensure bot is added as admin to the log channel

### Download Links Not Working
- Verify `RENDER_EXTERNAL_URL` is set correctly
- Check if web server is running (visit the health check endpoint `/`)
- Ensure the message ID exists in the log channel

### File Upload Errors
- Check file size (max 2GB for regular users, 4GB for Premium)
- Ensure bot has permission to forward messages to log channel
- Verify channel ID is correct (should be negative)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

Created with ❤️ by Tom2001moT

## 🌟 Support

If you found this project helpful, please give it a ⭐ on GitHub!

## 📞 Contact

- GitHub: [@Tom2001moT](https://github.com/Tom2001moT)
- Telegram: [Create an issue](https://github.com/Tom2001moT/File_To_Link/issues)

---

**Note**: This bot is for educational and personal use. Make sure you comply with Telegram's Terms of Service when using it.