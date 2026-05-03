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
                shortlink TEXT UNIQUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Try to upgrade older databases
        try:
            await db.execute("ALTER TABLE files ADD COLUMN shortlink TEXT;")
            await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_files_shortlink ON files(shortlink);")
        except Exception:
            pass
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

async def get_file_by_identifier(identifier):
    async with aiosqlite.connect(DB_NAME) as db:
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            async with db.execute("SELECT * FROM files WHERE message_id = ?", (int(identifier),)) as cursor:
                row = await cursor.fetchone()
                if row: return row
        
        # Fallback to checking by shortlink
        async with db.execute("SELECT * FROM files WHERE shortlink = ?", (str(identifier),)) as cursor:
            return await cursor.fetchone()

async def set_shortlink(message_id, shortlink):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute("UPDATE files SET shortlink = ? WHERE message_id = ?", (shortlink, message_id))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

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
