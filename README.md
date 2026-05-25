# FileToLink Bot 🔗 — Secure Cloud Engine

A powerful, high-performance Telegram bot that converts files into direct download links and real-time streaming services with **24/7 uptime**. Upload any file (video, audio, image, or document) directly to the bot and instantly receive a highly stylized, responsive, glassmorphic landing page containing embedded players, dynamic neon theme engines, live security integrity scanners, and QR code sharing interfaces.

Designed with asynchronous chunk-by-chunk media pipelines, the application streams files directly from Telegram's MTProto servers to the web client, bypassing physical host storage and allowing rapid downloads with minimal RAM usage.

---

## 🌟 Core Features

### 🤖 Telegram Bot Features
*   **Permanent Storage**: Uploads are securely forwarded to a private log channel which acts as an unlimited data center.
*   **SQLite Database Backend**: Manages active user records, download stats, and custom shortlink mappings persistently.
*   **Custom Shortlink Aliases (`/short`)**: Define elegant, human-readable routes for your file previews and downloads (e.g., `/view/my_video` instead of `/view/1042`).
*   **Individual File Manager (`/myfiles`)**: Instantly retrieve your last 50 uploads with active download metrics and direct preview links.
*   **Admin Utilities**:
    *   `/users`: Check active user statistics.
    *   `/broadcast [message]`: Instantly send alerts/messages to all users registered in the system.
*   **Advanced Status Engine (`/status`)**: Live diagnostic console tracking process uptime, log channel status, and total metrics.

### 🌐 Neon Web Landing Page Features
*   **Glassmorphic Aesthetic UI**: Premium design styled with custom Google Fonts (`Space Grotesk` & `Plus Jakarta Sans`), subtle background particle gradients, and glow effects.
*   **Simulated Cloud Integrity Scanner**: Interactive load widget checking SSL/TLS handshakes and simulating real-time file trust checks before unlocking downloads to wow users.
*   **Interactive Multi-Theme Switcher**: Select between 4 vibrant, high-fidelity neon themes stored locally in `localStorage`:
    *   🎨 **Cyber Cyan**: Sleek futuristic teal and magenta gradients.
    *   🎨 **Sunburst Neon**: High-energy red, orange, and yellow hues.
    *   🎨 **Toxic Emerald**: Acid green and deep amber elements.
    *   🎨 **Deep Amethyst**: Premium violet, amethyst, and pink tones.
*   **Native Inline Media Players**:
    *   🎥 **Video Stream**: HTML5 video element with seek capabilities.
    *   🎵 **Audio Stream**: Clean audio controller widget.
    *   🖼️ **Image Preview**: Dynamic picture display for graphic media.
    *   📄 **Tailored Document Previews**: Custom icons (`📦`, `📕`, `📄`, `📁`) optimized for ZIPs, PDFs, texts, and general archives.
*   **Dynamic Theme-Matched QR Codes**: Scannable mobile-friendly QR codes generated dynamically matching the exact theme colors of the browser.
*   **Utility actions Grid**: Instant copy buttons (Web Link, Direct Download Link), Telegram share API hook, and mobile QR modal trigger.

---

## ⚙️ Technical Stack

*   **Python 3.8+** — Asynchronous application runtime.
*   **Pyrogram 2.0.106 (MTProto Engine)** — High-speed API framework for Telegram network communication.
*   **Aiohttp 3.9+** — Asynchronous web server handling range requests and direct client streams.
*   **aiosqlite** — Asynchronous SQLite wrapper for non-blocking database queries.
*   **TgCrypto 1.2+** — High-performance C-based cryptographic encryption library for MTProto pipelines.
*   **qrcode** — Local QR matrix generator.
*   **QRServer API** — High-speed dynamic SVG/PNG theme matching client-side QR renderer.

---

## 📋 Prerequisites

Before setting up, make sure you have:

1.  **Telegram Account**: Access to create a bot and secure API keys.
2.  **API Credentials** (from [my.telegram.org](https://my.telegram.org)):
    *   `API_ID`: Numerical ID identifying your application context.
    *   `API_HASH`: Cryptographic hex string for MTProto authentication.
3.  **Bot Token** (from [@BotFather](https://t.me/BotFather)): Authenticates your bot with Telegram.
4.  **Private Storage Channel**: A Telegram channel created by you to store forwarded files safely.
5.  **Admin Access**: The bot **MUST** be added as an Administrator in your storage channel with **"Post Messages"** permissions enabled.

---

## 🛠️ Step-by-Step Local Setup

Follow these exact steps to run the project locally on your machine.

### Step 1: Clone the Repository
Open your terminal/shell and run:
```bash
git clone https://github.com/Tom2001moT/File_To_Link.git
cd File_To_Link
```

### Step 2: Establish Virtual Environment
Create a clean environment to isolate Python dependencies:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the required packages using `pip`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Local Environment Variables
Create a file named `.env` in the root directory:
```env
# --- Telegram API credentials ---
API_ID=1234567               # Replace with your Telegram API ID (integer)
API_HASH=your_api_hash_here  # Replace with your Telegram API Hash (string)
BOT_TOKEN=12345:ABCde...     # Replace with your bot token from @BotFather

# --- Private Storage Channel ID or Username ---
# For channel IDs, make sure to include the "-100" prefix (e.g. -1001928374650)
LOG_CHANNEL=-1001234567890

# --- Administration Settings ---
ADMIN_ID=987654321           # Replace with your numerical Telegram User ID

# --- Server Configurations ---
PORT=8080
RENDER_EXTERNAL_URL=http://localhost:8080
```

> [!IMPORTANT]
> Double-check your `LOG_CHANNEL` ID. If you copy a channel ID, it must start with a minus sign (typically `-100...`). Adding the bot as an administrator of this channel is crucial before running!

### Step 5: Start the Bot
Execute the main entry script to start services:
```bash
python main.py
```

Upon starting, you will see initialization logs:
```text
--- [INFO] Starting Telegram Client ---
--- [INFO] Attempting to resolve Log Channel: -1001234567890 ---
--- [SUCCESS] Log Channel Resolved: Secure File Storage ---
--- [INFO] Web Server running on port 8080 ---
--- [INFO] Starting 24/7 Keep-Alive for http://localhost:8080 ---
```

---

## 🌐 Production Deployment Guide (Render.com)

Render is highly recommended due to native Python web service support and a robust Free Tier.

### Step 1: Prepare and Push to GitHub
1.  Fork this repository to your own GitHub account.
2.  Commit your work (ensure your local `.env` and `bot_data.db` database are in `.gitignore` to keep tokens safe).

### Step 2: Set Up a Render Web Service
1.  Go to the [Render Dashboard](https://dashboard.render.com/) and sign up/login with GitHub.
2.  Click **New +** -> **Web Service**.
3.  Select your forked `File_To_Link` repository and click **Connect**.

### Step 3: Configure Settings
Fill out the service parameters exactly as follows:
*   **Name**: `file-to-link-service` (or any unique identifier).
*   **Region**: Select the server location closest to your audience.
*   **Branch**: `main`.
*   **Runtime**: `Python 3`.
*   **Build Command**: `pip install -r requirements.txt`.
*   **Start Command**: `python main.py`.
*   **Instance Type**: `Free`.

### Step 4: Configure Environment Variables
Click on **Advanced** -> **Add Environment Variable** and key in your parameters:

| Environment Key | Recommended Value | Description |
| :--- | :--- | :--- |
| `API_ID` | `Your API ID` | Numerical credentials from Telegram. |
| `API_HASH` | `Your API Hash` | Hex authentication token. |
| `BOT_TOKEN` | `Your Bot Token` | Bot credential from @BotFather. |
| `LOG_CHANNEL` | `-100...` | Your private storage channel ID. |
| `ADMIN_ID` | `Your User ID` | Numerical User ID to enable Admin controls. |
| `PORT` | `8080` | Local network binding port. |

### Step 5: Save & Deploy
1.  Click **Create Web Service**.
2.  Render will pull the codebase, set up Python dependencies, build metadata, and spin up the bot.
3.  Wait until the logs read: `Web Server running on port 8080`.
4.  Copy your public service URL from the top of the Render page (e.g. `https://file-to-link-service.onrender.com`).

### Step 6: Add External URL for Streaming & Self-Pings
1.  Go back to the **Environment** tab on your Render dashboard.
2.  Add a new environment variable:
    *   **Key**: `RENDER_EXTERNAL_URL`
    *   **Value**: `https://file-to-link-service.onrender.com` (your exact copied URL).
3.  Click **Save Changes**. This will trigger an automatic clean redeploy. Your links and pings are now fully active!

---

## ⏰ Maintaining 24/7 Keep-Alive Uptime

Render's Free tier spins down web services after 15 minutes of inbound traffic inactivity. While the bot has an internal ping task running in the background, combining it with an external cron service guarantees maximum availability.

### Option A: UptimeRobot (Highly Recommended)
1.  Create a free account on [UptimeRobot](https://uptimerobot.com/).
2.  Click **Add New Monitor**:
    *   **Monitor Type**: `HTTP(s)`
    *   **Friendly Name**: `FileToLink Cloud KeepAlive`
    *   **URL (or IP)**: `https://your-service-name.onrender.com/` (your Render URL)
    *   **Monitoring Interval**: Every 5 minutes.
3.  Click **Create Monitor**.

### Option B: Cron-Job.org
1.  Sign up on [Cron-Job.org](https://cron-job.org/).
2.  Create a new cronjob:
    *   **Title**: `FileToLink Ping`
    *   **Address**: `https://your-service-name.onrender.com/`
    *   **Schedule**: Every 10 minutes.
3.  Save the cron configuration.

---

## 🤖 Bot Command Directory

| Command | Allowed Users | Description / Usage Syntax | Expected Bot Action |
| :--- | :--- | :--- | :--- |
| `/start` | All Users | `/start` | Registers user in database, displays rich welcome console. |
| `/help` | All Users | `/help` | Details structural guidelines on uploading and configuring. |
| `/about` | All Users | `/about` | Information about development metrics and developers. |
| `/status` | All Users | `/status` | Renders a system check showing server status, uptime, and database records. |
| `/myfiles` | All Users | `/myfiles` | Retrieves user's last 50 uploaded files, showcasing download counts. |
| `/short` | All Users | `/short [alias_name]` *(sent as reply to a generated link)* | Connects file to a permanent shortened alias. |
| `/users` | Admins Only | `/users` | Displays the total count of registered users in the database. |
| `/broadcast` | Admins Only | `/broadcast [your custom message text]` | Instantly relays administrative announcements to all users. |

---

## 🔧 Architecture & Media Streaming Pipeline

```text
  [ User ] --------( Send Media File )-------> [ Telegram Bot UI ]
                                                     │
                                             ( Forward Copy )
                                                     ▼
                                            [ Private Log Channel ]
                                                     │
                                            ( Registers Message ID )
                                                     ▼
                                             [ SQLite DB Index ]
                                                     │
                                              ( Generates URL )
                                                     ▼
  [ Web Client ] <---( Direct Chunk Stream )---- [ Aiohttp Server ]
```

1.  **Stateless Storage**: When you upload a file, the bot utilizes the fast MTProto API `copy_message` method to clone the file instantly into your private storage channel. It doesn't write anything locally to the server's hard disk, making it lightweight and highly secure.
2.  **Streaming Middleware**: When a user clicks the direct link `/dl/{id}` or streams via the embedded audio/video player `/stream/{id}`, the Aiohttp server intercepts the call.
3.  **HTTP Range Requests**: The server reads the client's requested byte ranges (e.g. `Range: bytes=1048576-2097152`), calls Pyrogram's `stream_media` generator tool in the background, pulls that exact chunk directly from Telegram servers on-the-fly, and serves it immediately. This allows seamless video scrubbing and audio seeking on modern mobile and desktop browsers without storing the actual video file!

---

## 👨‍💻 Developer & Credits

*   **Developer**: [@WhiteDeathGaming](https://t.me/WhiteDeathGaming) **WDG**
*   **GitHub Repository**: [Tom2001moT/File_To_Link](https://github.com/Tom2001moT)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.