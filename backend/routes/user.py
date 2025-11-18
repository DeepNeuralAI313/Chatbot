from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from models.user import UserSignup, UserLogin, UserResponse, ConversationListItem
from database.db import (
    create_user, verify_user_credentials, get_user_by_email,
    get_user_conversations, get_conversation_messages
)
import os

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user_id"""
    try:
        token = credentials.credentials
        print(f"Verifying token: {token[:20]}...")  # Debug log
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        print(f"Token decoded, user_id: {user_id}")  # Debug log
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except JWTError as e:
        print(f"JWT Error: {e}")  # Debug log
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        print(f"Token verification error: {e}")  # Debug log
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/api/user/signup", response_model=UserResponse)
async def signup(request: UserSignup):
    """User signup endpoint"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = create_user(request.email, request.name, request.password)
        
        # Create access token
        access_token = create_access_token(data={"user_id": user_id, "email": request.email})
        
        return UserResponse(
            id=user_id,
            email=request.email,
            name=request.name,
            token=access_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in signup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user/login", response_model=UserResponse)
async def login(request: UserLogin):
    """User login endpoint"""
    try:
        # Verify credentials
        user = verify_user_credentials(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = create_access_token(data={"user_id": user["id"], "email": user["email"]})
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            token=access_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/user/conversations")
async def get_conversations(user_id: int = Depends(verify_user_token)):
    """Get all conversations for the authenticated user"""
    try:
        conversations = get_user_conversations(user_id)
        return {"conversations": conversations}
    except Exception as e:
        print(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/user/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, user_id: int = Depends(verify_user_token)):
    """Get all messages for a specific conversation"""
    try:
        messages = get_conversation_messages(conversation_id)
        return messages
    except Exception as e:
        print(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
