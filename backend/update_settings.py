import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "chatbot.db"

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Update fallback message
cursor.execute("""
    UPDATE settings 
    SET value = 'I don''t have specific information about that in my knowledge base, but I''d be happy to help with general questions or other topics!' 
    WHERE key = 'fallback_message'
""")

# Update tone instructions
cursor.execute("""
    UPDATE settings 
    SET value = 'You are a helpful, friendly AI assistant. Always try to answer questions based on the context provided. If the context doesn''t contain the exact answer, use your general knowledge to provide a helpful response. Be conversational, warm, and informative. Keep responses clear and concise but comprehensive. If you truly cannot answer something, politely say so and ask if there''s another way you can help.' 
    WHERE key = 'tone_instructions'
""")

conn.commit()
conn.close()

print("Settings updated successfully!")
print("Please restart the backend server for changes to take effect.")
