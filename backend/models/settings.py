from pydantic import BaseModel

class Settings(BaseModel):
    welcome_message: str
    fallback_message: str
    tone_instructions: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str
