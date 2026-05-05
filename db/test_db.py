import sqlite3
import os

DB_PATH = "test_crm.db"

def get_db_connection():
    """
    Returns a connection to the local test SQLite database.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_test_db():
    """
    Initializes the local SQLite database with testing tables and mock data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create mock tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'premium',
            name TEXT
        );

        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT NOT NULL,
            asset_type TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    ''')
    
    # Insert dummy user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE email='test@investor.com'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (email, name) VALUES ('test@investor.com', 'Inversor Beta')")
        cursor.execute("INSERT INTO watchlists (user_id, symbol, asset_type) VALUES (1, 'GC=F', 'commodity')") # Gold
        cursor.execute("INSERT INTO watchlists (user_id, symbol, asset_type) VALUES (1, 'CL=F', 'commodity')") # Crude Oil
    
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    init_test_db()
    print("Test Database Initialized at test_crm.db")
