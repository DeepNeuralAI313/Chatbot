from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignup(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    token: str

class ConversationListItem(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int
    last_message_at: Optional[str]
