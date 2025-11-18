import sqlite3
import os
from pathlib import Path
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PATH = Path(__file__).parent / "chatbot.db"

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables and default data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_tokens_used INTEGER DEFAULT 0
        )
    """)
    
    # Create conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Migrate existing conversations table if needed
    try:
        cursor.execute("SELECT user_id FROM conversations LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        print("Migrating conversations table: adding user_id column")
        cursor.execute("ALTER TABLE conversations ADD COLUMN user_id INTEGER")
    
    try:
        cursor.execute("SELECT title FROM conversations LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        print("Migrating conversations table: adding title column")
        cursor.execute("ALTER TABLE conversations ADD COLUMN title TEXT")
    
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    
    # Create token_usage table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            user_id INTEGER,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            cost REAL DEFAULT 0.0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Create settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Create admin_users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            hashed_password TEXT
        )
    """)
    
    # Insert default settings if not exist
    default_settings = {
        "welcome_message": "Hello! How can I help you today?",
        "fallback_message": "I don't have specific information about that in my knowledge base, but I'd be happy to help with general questions or other topics!",
        "tone_instructions": "You are a helpful, friendly human assistant (not a bot). Write in a natural, conversational style like you're chatting with a friend. Use contractions (I'm, you're, that's), casual language, and vary your sentence structure. Don't use numbered lists unless specifically asked. Instead, write in flowing paragraphs with natural transitions. Be warm, personable, and genuine. When explaining things, break them into easy-to-understand chunks within your natural conversation flow. Avoid robotic phrases like 'Here is' or 'The answer is'. Just talk naturally!"
    }
    
    for key, value in default_settings.items():
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    # Insert default admin user (username: admin, password: admin123)
    default_admin_username = "admin"
    default_admin_password = "admin123"
    hashed_password = pwd_context.hash(default_admin_password)
    
    cursor.execute(
        "INSERT OR IGNORE INTO admin_users (username, hashed_password) VALUES (?, ?)",
        (default_admin_username, hashed_password)
    )
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def get_setting(key: str) -> str:
    """Get a setting value by key"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result["value"] if result else None

def update_setting(key: str, value: str):
    """Update a setting value"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

def save_conversation(conversation_id: str):
    """Create a new conversation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO conversations (id, created_at) VALUES (?, ?)",
        (conversation_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def save_message(conversation_id: str, role: str, content: str):
    """Save a message to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_conversation_history(conversation_id: str):
    """Get all messages for a conversation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
        (conversation_id,)
    )
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin login credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT hashed_password FROM admin_users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return False
    
    return pwd_context.verify(password, result["hashed_password"])

# User management functions
def create_user(email: str, name: str, password: str) -> int:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(password)
    cursor.execute(
        "INSERT INTO users (email, name, hashed_password) VALUES (?, ?, ?)",
        (email, name, hashed_password)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email: str):
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def verify_user_credentials(email: str, password: str):
    """Verify user login credentials"""
    user = get_user_by_email(email)
    if user is None:
        return None
    
    if pwd_context.verify(password, user["hashed_password"]):
        return user
    return None

def get_user_conversations(user_id: int):
    """Get all conversations for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.title, c.created_at, 
               COUNT(m.id) as message_count,
               MAX(m.timestamp) as last_message_at
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.user_id = ?
        GROUP BY c.id
        ORDER BY last_message_at DESC
    """, (user_id,))
    conversations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return conversations

def save_conversation_with_user(conversation_id: str, user_id: int, title: str = None):
    """Create a new conversation for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO conversations (id, user_id, title, created_at) VALUES (?, ?, ?, ?)",
        (conversation_id, user_id, title or "New Conversation", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def update_conversation_title(conversation_id: str, title: str):
    """Update conversation title"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET title = ? WHERE id = ?",
        (title, conversation_id)
    )
    conn.commit()
    conn.close()

def get_conversation_messages(conversation_id: str):
    """Get all messages for a conversation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
    """, (conversation_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def save_token_usage(conversation_id: str, user_id: int, prompt_tokens: int, completion_tokens: int, total_tokens: int, cost: float):
    """Save token usage information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO token_usage (conversation_id, user_id, prompt_tokens, completion_tokens, total_tokens, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (conversation_id, user_id, prompt_tokens, completion_tokens, total_tokens, cost, datetime.now().isoformat()))
    
    # Update user's total tokens
    cursor.execute("""
        UPDATE users SET total_tokens_used = total_tokens_used + ? WHERE id = ?
    """, (total_tokens, user_id))
    
    conn.commit()
    conn.close()

def get_all_users_with_stats():
    """Get all users with their stats"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            u.id, u.email, u.name, u.created_at, u.total_tokens_used,
            COUNT(DISTINCT c.id) as conversation_count,
            SUM(t.cost) as total_cost
        FROM users u
        LEFT JOIN conversations c ON u.id = c.user_id
        LEFT JOIN token_usage t ON u.id = t.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_total_app_stats():
    """Get total application statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total tokens
    cursor.execute("SELECT SUM(total_tokens_used) as total_tokens FROM users")
    total_tokens = cursor.fetchone()["total_tokens"] or 0
    
    # Total cost
    cursor.execute("SELECT SUM(cost) as total_cost FROM token_usage")
    total_cost = cursor.fetchone()["total_cost"] or 0.0
    
    # Total users
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()["total_users"]
    
    # Total conversations
    cursor.execute("SELECT COUNT(*) as total_conversations FROM conversations")
    total_conversations = cursor.fetchone()["total_conversations"]
    
    conn.close()
    return {
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
        "total_users": total_users,
        "total_conversations": total_conversations
    }

def get_usage_over_time():
    """Get token usage over time for graphs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            DATE(timestamp) as date,
            SUM(total_tokens) as tokens,
            SUM(cost) as cost,
            COUNT(*) as requests
        FROM token_usage
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 30
    """)
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

