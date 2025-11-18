import sqlite3
import os

def update_settings():
    # Use the database in the database folder (same as the application uses)
    db_path = os.path.join('database', 'chatbot.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update settings with more human-like instructions
    new_tone = """You are a helpful, friendly human assistant (not a bot). Write in a natural, conversational style like you're chatting with a friend. Use contractions (I'm, you're, that's), casual language, and vary your sentence structure. Don't use numbered lists unless specifically asked. Instead, write in flowing paragraphs with natural transitions. Be warm, personable, and genuine. When explaining things, break them into easy-to-understand chunks within your natural conversation flow. Avoid robotic phrases like 'Here is' or 'The answer is'. Just talk naturally!"""
    
    new_fallback = """I don't have specific information about that in my knowledge base, but I'd be happy to help with general questions or other topics!"""
    
    # Update using key-value structure
    cursor.execute("""
        UPDATE settings 
        SET value = ?
        WHERE key = 'tone_instructions'
    """, (new_tone,))
    
    cursor.execute("""
        UPDATE settings 
        SET value = ?
        WHERE key = 'fallback_message'
    """, (new_fallback,))
    
    conn.commit()
    conn.close()
    
    print("✅ Settings updated successfully!")
    print("✨ The AI will now respond in a more natural, human-like way")
    print("📝 Conversation titles will be generated more intelligently")
    print(f"\n📁 Updated database: {db_path}")
    print("🔄 The backend should auto-reload with these changes")

if __name__ == "__main__":
    update_settings()
