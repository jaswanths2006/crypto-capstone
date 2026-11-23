# SQLite database configuration and schema setup for SIOTDA backend
import sqlite3
import os

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/iot_security.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "iot_security.db")

_initialized = False

# Establishes database connection with row access by column name
def get_db():
    global _initialized
    if not _initialized and not os.path.exists(DB_PATH):
        init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.OperationalError:
        pass
    return conn

# Initializes database tables required for IoT authentication and communication
def init_db():
    global _initialized
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Stores registered IoT devices with pre-shared keys
    c.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id    TEXT PRIMARY KEY,
            psk          TEXT NOT NULL,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Stores nonce values used in authentication challenges to prevent replay attacks
    c.execute("""
        CREATE TABLE IF NOT EXISTS nonces (
            nonce       TEXT PRIMARY KEY,
            device_id   TEXT NOT NULL,
            created_at  REAL NOT NULL,
            used        INTEGER DEFAULT 0,
            ttl         INTEGER DEFAULT 30,
            FOREIGN KEY(device_id) REFERENCES devices(device_id)
        )
    """)

    # Stores session tokens issued after successful authentication
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token       TEXT PRIMARY KEY,
            device_id   TEXT NOT NULL,
            created_at  REAL NOT NULL,
            expires_at  REAL NOT NULL
        )
    """)

    # Stores encrypted messages exchanged between devices
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender      TEXT NOT NULL,
            receiver    TEXT NOT NULL,
            ciphertext  TEXT NOT NULL,
            iv          TEXT NOT NULL,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Stores security-related events such as authentication attempts and attacks
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
            event       TEXT NOT NULL,
            device      TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    _initialized = True