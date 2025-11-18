from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    needs_human: bool
    conversation_id: str

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Message]
