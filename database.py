import aiosqlite
import logging

logger = logging.getLogger("db")

DB_NAME = "bot_data.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Files table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_id INTEGER,
                filename TEXT,
                file_size INTEGER,
                downloads INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
        logger.info("Database initialized.")

async def add_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def add_file(user_id, message_id, filename, file_size):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "INSERT INTO files (user_id, message_id, filename, file_size) VALUES (?, ?, ?, ?)",
            (user_id, message_id, filename, file_size)
        )
        await db.commit()
        return cursor.lastrowid

async def get_file_by_message_id(message_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM files WHERE message_id = ?", (message_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_files(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT message_id, filename, downloads FROM files WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id,)) as cursor:
            return await cursor.fetchall()

async def increment_download(message_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE files SET downloads = downloads + 1 WHERE message_id = ?", (message_id,))
        await db.commit()

async def get_total_downloads():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT SUM(downloads) FROM files") as cursor:
            row = await cursor.fetchone()
            return row[0] if row[0] else 0
