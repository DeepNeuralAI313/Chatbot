from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from models.settings import Settings, LoginRequest, LoginResponse
from database.db import (
    get_setting, update_setting, verify_admin_credentials,
    get_all_users_with_stats, get_total_app_stats, get_usage_over_time
)
import os

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/api/admin/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Admin login endpoint
    """
    try:
        # Verify credentials
        if not verify_admin_credentials(request.username, request.password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create access token
        access_token = create_access_token(data={"sub": request.username})
        
        return LoginResponse(
            token=access_token,
            username=request.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/settings", response_model=Settings)
async def get_settings():
    """
    Get admin settings (public endpoint for welcome messages)
    """
    try:
        welcome_message = get_setting("welcome_message")
        fallback_message = get_setting("fallback_message")
        tone_instructions = get_setting("tone_instructions")
        
        return Settings(
            welcome_message=welcome_message,
            fallback_message=fallback_message,
            tone_instructions=tone_instructions
        )
    
    except Exception as e:
        print(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/admin/settings", response_model=Settings)
async def update_settings(settings: Settings, username: str = Depends(verify_token)):
    """
    Update admin settings
    """
    try:
        update_setting("welcome_message", settings.welcome_message)
        update_setting("fallback_message", settings.fallback_message)
        update_setting("tone_instructions", settings.tone_instructions)
        
        return settings
    
    except Exception as e:
        print(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/users")
async def get_users(username: str = Depends(verify_token)):
    """
    Get all users with statistics
    """
    try:
        users = get_all_users_with_stats()
        return {"users": users}
    except Exception as e:
        print(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/stats")
async def get_stats(username: str = Depends(verify_token)):
    """
    Get total application statistics
    """
    try:
        stats = get_total_app_stats()
        return stats
    except Exception as e:
        print(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/admin/usage-over-time")
async def get_usage(username: str = Depends(verify_token)):
    """
    Get usage data over time for graphs
    """
    try:
        usage_data = get_usage_over_time()
        return {"usage": usage_data}
    except Exception as e:
        print(f"Error getting usage data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
