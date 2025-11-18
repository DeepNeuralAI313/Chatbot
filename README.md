# Mini AI Chatbot System

A full-stack AI chatbot system with RAG (Retrieval Augmented Generation), admin panel, and human escalation logic built with **FastAPI** (backend) and **React** (frontend).

## 🎯 Project Overview

This chatbot system provides:
- **RAG-powered responses** using OpenAI embeddings and GPT
- **Knowledge base** from Wikipedia article about IPTV
- **Admin panel** to customize chatbot behavior
- **Human handoff** for escalation keywords
- **Conversation history** stored in SQLite
- **Floating chat widget** with modern UI

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with Vite
- **Database**: SQLite
- **Vector Store**: ChromaDB
- **LLM**: OpenAI GPT-3.5/4
- **Embeddings**: OpenAI text-embedding-ada-002

## 📁 Project Structure

```
chatbot_test_task/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   ├── conversation.py     # Pydantic models for chat
│   │   └── settings.py         # Pydantic models for admin
│   ├── services/
│   │   ├── rag_service.py      # RAG implementation
│   │   ├── llm_service.py      # OpenAI GPT integration
│   │   └── embedding_service.py # OpenAI embeddings
│   ├── routes/
│   │   ├── chat.py             # Chat endpoint
│   │   ├── admin.py            # Admin endpoints
│   │   └── conversation.py     # Conversation history
│   ├── database/
│   │   ├── db.py               # Database operations
│   │   └── chatbot.db          # SQLite database (created on startup)
│   └── data/
│       └── article.txt         # Knowledge base
├── chat-ui/                    # Chat widget React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWidget.jsx
│   │   │   ├── ChatBubble.jsx
│   │   │   └── ChatInput.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   └── package.json
├── admin/                      # Admin panel React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── SettingsForm.jsx
│   │   ├── services/
│   │   │   └── adminApi.js
│   │   └── App.jsx
│   └── package.json
├── .env.example
└── README.md
```

## ✨ Features

### 1. RAG System
- Loads article about IPTV from Wikipedia
- Chunks text into 400-character segments with overlap
- Generates embeddings using OpenAI
- Performs vector similarity search
- Retrieves top 3 relevant chunks for context

### 2. Chat Functionality
- **Welcome Message**: Customizable greeting
- **Smart Responses**: Context-aware answers using RAG + GPT
- **Fallback Handling**: Custom message when similarity is low (<0.6)
- **Escalation Detection**: Keywords trigger human handoff
  - `refund`, `money back`, `return`, `bani înapoi`, `restituire`
- **Conversation Storage**: All messages saved to SQLite
- **Romanian Support**: Designed for Romanian language

### 3. Admin Panel
- **Secure Login**: JWT authentication (username: `admin`, password: `admin123`)
- **Three Configurable Settings**:
  1. **Welcome Message**: First message in chat
  2. **Fallback Message**: When AI can't find info
  3. **Tone Instructions**: System prompt for GPT
- **Real-time Updates**: Changes apply immediately

### 4. Chat UI
- Floating chat button (bottom-right)
- Expandable chat window (350px × 500px)
- User/Assistant message bubbles
- Typing indicator
- Timestamp on messages
- Human handoff notification
- Mobile responsive

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### 1. Backend Setup

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item ..\.env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
notepad .env

# Run the backend server
python main.py
```

Backend will run on: **http://localhost:8000**

### 2. Chat UI Setup

```powershell
# Open new terminal
cd chat-ui

# Install dependencies
npm install

# Run development server
npm run dev
```

Chat UI will run on: **http://localhost:5173**

### 3. Admin Panel Setup

```powershell
# Open new terminal
cd admin

# Install dependencies
npm install

# Run development server
npm run dev
```

Admin Panel will run on: **http://localhost:5174**

## 🔑 Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

## 📝 Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

## 🎮 Usage Guide

### Using the Chat Widget

1. Open **http://localhost:5173** in your browser
2. Click the floating chat button (purple circle, bottom-right)
3. Chat widget opens with welcome message
4. Type IPTV-related questions:
   - "What is IPTV?"
   - "How does IPTV work?"
   - "What are the benefits of IPTV?"
5. To test escalation, type: "I want a refund"
6. Chat will display: "AI a oprit. Un coleg va prelua conversația."

### Using the Admin Panel

1. Open **http://localhost:5174** in your browser
2. Login with credentials (`admin` / `admin123`)
3. Edit the three settings:
   - **Welcome Message**: Greeting shown on chat open
   - **Fallback Message**: Response when AI doesn't know
   - **Tone Instructions**: How AI should behave
4. Click "Save Settings"
5. Changes apply immediately to new conversations

## 🔌 API Endpoints

### Chat Endpoints

**POST** `/api/chat`
```json
Request:
{
  "message": "What is IPTV?",
  "conversation_id": "optional-uuid"
}

Response:
{
  "reply": "IPTV is Internet Protocol television...",
  "needs_human": false,
  "conversation_id": "uuid"
}
```

**GET** `/api/conversation/{conversation_id}`
```json
Response:
{
  "conversation_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "What is IPTV?",
      "timestamp": "2025-11-17T10:30:00"
    }
  ]
}
```

### Admin Endpoints

**POST** `/api/admin/login`
```json
Request:
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "token": "jwt_token",
  "username": "admin"
}
```

**GET** `/api/admin/settings` (requires JWT)
```json
Response:
{
  "welcome_message": "Bună! Cum te pot ajuta astăzi cu IPTV?",
  "fallback_message": "Ne pare rău, nu am găsit informații...",
  "tone_instructions": "You are a friendly assistant..."
}
```

**POST** `/api/admin/settings` (requires JWT)
```json
Request:
{
  "welcome_message": "New message",
  "fallback_message": "New fallback",
  "tone_instructions": "New instructions"
}
```

## 📊 Database Schema

### Tables

**conversations**
- `id`: TEXT (PRIMARY KEY)
- `created_at`: TIMESTAMP

**messages**
- `id`: INTEGER (PRIMARY KEY)
- `conversation_id`: TEXT (FOREIGN KEY)
- `role`: TEXT (`user` or `assistant`)
- `content`: TEXT
- `timestamp`: TIMESTAMP

**settings**
- `key`: TEXT (PRIMARY KEY)
- `value`: TEXT

**admin_users**
- `id`: INTEGER (PRIMARY KEY)
- `username`: TEXT (UNIQUE)
- `hashed_password`: TEXT

## 🧪 Testing the System

### Test RAG Functionality
Ask questions about IPTV:
- "What is IPTV?"
- "How does IPTV work?"
- "What are the benefits?"
- "Can I watch on mobile?"

### Test Fallback Message
Ask unrelated questions:
- "What is the weather?"
- "Tell me about cars"

### Test Escalation
Type escalation keywords:
- "I want a refund"
- "money back"
- "bani înapoi"

### Test Admin Settings
1. Change welcome message in admin panel
2. Open new chat (or clear localStorage)
3. Verify new welcome message appears

## 🎨 Customization

### Change Chatbot Colors
Edit `chat-ui/src/components/ChatWidget.css`:
```css
.floating-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Change Knowledge Base
Replace `backend/data/article.txt` with your content, then restart backend.

### Add More Escalation Keywords
Edit `backend/routes/chat.py`:
```python
def check_escalation(message: str) -> bool:
    keywords = ['refund', 'money back', 'your_keyword']
    return any(keyword in message.lower() for keyword in keywords)
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.8+)
- Verify OpenAI API key in `.env`
- Check if port 8000 is available

### Chat UI shows errors
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify proxy settings in `vite.config.js`

### Admin login fails
- Default credentials: `admin` / `admin123`
- Check if backend is running
- Look for JWT errors in backend logs

### RAG not working
- Verify `backend/data/article.txt` exists
- Check OpenAI API key is valid
- Look for embedding errors in backend logs

## 📦 Building for Production

### Backend
```powershell
cd backend
pip install -r requirements.txt
# Use gunicorn or uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```powershell
# Chat UI
cd chat-ui
npm run build
# Serve the dist/ folder

# Admin Panel
cd admin
npm run build
# Serve the dist/ folder
```

## 🔒 Security Notes

⚠️ **Important for Production:**
1. Change `JWT_SECRET_KEY` in `.env`
2. Change default admin password
3. Use HTTPS for all connections
4. Set specific CORS origins (not `*`)
5. Add rate limiting
6. Use environment-specific configs

## 📄 License

This project is created for demonstration purposes.

## 🤝 Support

For issues or questions, please check:
- Backend logs in terminal
- Browser console (F12)
- Network tab for API errors

---

