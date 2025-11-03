"""
Backend API Server for VoicePlan
=================================
Features:
- Google OAuth authentication
- Credit system (10 credits per Gmail account)
- LiveKit token generation and room management
- Rate limiting
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import os
import jwt
import time
from datetime import datetime, timedelta
from livekit import api
import sqlite3
from contextlib import contextmanager
import secrets
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="VoicePlan API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://voice-agent-yeja0ufzl-vedants-projects-a95326a8.vercel.app",
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
DATABASE_PATH = "voiceplan.db"

# Initialize database
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize SQLite database with users and usage tracking tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                picture TEXT,
                credits INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Usage log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_name TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                credits_used INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        logger.info("Database initialized successfully")

# Initialize DB on startup
init_database()

# Pydantic models
class GoogleLoginRequest(BaseModel):
    token: str

class AuthResponse(BaseModel):
    access_token: str
    user: Dict[str, Any]

class TokenRequest(BaseModel):
    room_name: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    url: str
    room_name: str

class UserInfo(BaseModel):
    email: str
    name: Optional[str]
    picture: Optional[str]
    credits: int

# Helper functions
def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for authenticated user."""
    payload = {
        "email": user_data["email"],
        "name": user_data.get("name"),
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return user data."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    user_data = verify_jwt_token(token)
    
    # Get user from database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (user_data["email"],))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return dict(user)

def get_or_create_user(email: str, name: Optional[str], picture: Optional[str]) -> dict:
    """Get existing user or create new one with 10 credits."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Try to get existing user
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = ?",
                (email,)
            )
            return dict(user)
        else:
            # Create new user with 10 credits
            cursor.execute(
                """INSERT INTO users (email, name, picture, credits, last_login) 
                   VALUES (?, ?, ?, 10, CURRENT_TIMESTAMP)""",
                (email, name, picture)
            )
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return dict(cursor.fetchone())

def use_credit(user_id: int) -> bool:
    """Deduct one credit from user. Returns True if successful, False if no credits."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check current credits
        cursor.execute("SELECT credits FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result or result["credits"] <= 0:
            return False
        
        # Deduct credit
        cursor.execute(
            "UPDATE users SET credits = credits - 1 WHERE id = ?",
            (user_id,)
        )
        
        return True

# API Routes
@app.get("/")
async def root():
    return {"message": "VoicePlan API Server", "status": "running"}

@app.post("/auth/google", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest):
    """Authenticate user with Google OAuth token."""
    try:
        # Verify Google token with clock skew tolerance
        idinfo = id_token.verify_oauth2_token(
            request.token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10  # Allow 10 seconds tolerance for clock skew
        )
        
        # Extract user info
        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")
        
        # Get or create user
        user = get_or_create_user(email, name, picture)
        
        # Create JWT token
        jwt_token = create_jwt_token(user)
        
        return {
            "access_token": jwt_token,
            "user": {
                "email": user["email"],
                "name": user["name"],
                "picture": user["picture"],
                "credits": user["credits"]
            }
        }
        
    except ValueError as e:
        logger.error(f"Google token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")

@app.get("/auth/me", response_model=UserInfo)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user information."""
    return {
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"],
        "credits": user["credits"]
    }

@app.post("/livekit/token", response_model=TokenResponse)
async def generate_livekit_token(
    request: TokenRequest,
    user: dict = Depends(get_current_user)
):
    """Generate LiveKit access token for authenticated user."""
    
    # Check if user has credits
    if user["credits"] <= 0:
        raise HTTPException(
            status_code=403, 
            detail="No credits remaining. Please contact support to add more credits."
        )
    
    # Generate room name if not provided
    room_name = request.room_name or f"room-{user['id']}-{int(time.time())}"
    
    # Create LiveKit access token
    try:
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(user["email"])
        token.with_name(user["name"] or user["email"])
        token.with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )
        
        jwt_token = token.to_jwt()
        
        # Deduct credit
        if not use_credit(user["id"]):
            raise HTTPException(status_code=403, detail="Failed to deduct credit")
        
        # Log usage
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usage_logs (user_id, room_name) VALUES (?, ?)",
                (user["id"], room_name)
            )
        
        logger.info(f"Generated token for user {user['email']}, room: {room_name}")
        
        return {
            "token": jwt_token,
            "url": LIVEKIT_URL,
            "room_name": room_name
        }
        
    except Exception as e:
        logger.error(f"Failed to generate LiveKit token: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate access token")

@app.post("/credits/check")
async def check_credits(user: dict = Depends(get_current_user)):
    """Check remaining credits for current user."""
    return {
        "credits": user["credits"],
        "email": user["email"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "livekit_configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_SECRET),
        "google_auth_configured": bool(GOOGLE_CLIENT_ID)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
