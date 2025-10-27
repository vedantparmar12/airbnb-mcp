# VoicePlan - Setup Guide

Complete integration of LiveKit voice agent with authentication and credit system.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Frontend      │─────▶│  Backend API     │─────▶│   LiveKit       │
│   (Next.js)     │      │  (FastAPI)       │      │   Agent Server  │
│                 │      │                  │      │                 │
│ - Google OAuth  │      │ - Authentication │      │ - livekit_mcp_  │
│ - LiveKit UI    │      │ - Credit System  │      │   agent.py      │
│ - Credit Display│      │ - Token Gen      │      │ - Ollama/Groq   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   SQLite DB      │
                         │                  │
                         │ - Users          │
                         │ - Credits (10)   │
                         │ - Usage Logs     │
                         └──────────────────┘
```

## Features

✅ **Google OAuth Authentication** - Sign in with Gmail  
✅ **Credit System** - 10 free credits per Gmail account  
✅ **LiveKit Integration** - Continuous voice chat using `livekit_mcp_agent.py`  
✅ **Rate Limiting** - Tracks usage per user  
✅ **Real-time Voice** - Powered by Deepgram (STT) + Cartesia (TTS) + Ollama/Groq (LLM)  
✅ **MCP Airbnb Tools** - Search listings, compare prices, calculate budgets

## Prerequisites

1. **Node.js** (v18+) - for frontend
2. **Python** (3.10+) - for backend and agent
3. **LiveKit Server** - running locally or cloud
4. **Google OAuth** - Client ID from Google Cloud Console
5. **API Keys**:
   - Deepgram API key (STT)
   - Cartesia API key (TTS)
   - Groq API key (LLM fallback) OR Ollama running locally

## Step 1: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins:
   - `http://localhost:3000`
   - `http://localhost:3001`
7. Copy the **Client ID** (you'll need this)

## Step 2: Backend Setup

### Install Python Dependencies

```powershell
# Navigate to project root
cd C:\Users\vedan\Desktop\mcp-rag\voice-agent

# Install backend requirements
pip install -r backend_requirements.txt

# Install agent requirements (if not already done)
pip install -r requirements.txt
```

### Configure Backend Environment

```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit .env file with your values
notepad .env
```

Fill in these required values in `.env`:

```env
# LiveKit (from your LiveKit server)
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
LIVEKIT_URL=ws://localhost:7880

# Google OAuth (from Step 1)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# JWT Secret (generate random string)
JWT_SECRET=your-secret-random-string-change-this

# Voice AI APIs
DEEPGRAM_API_KEY=your-deepgram-api-key
CARTESIA_API_KEY=your-cartesia-api-key

# LLM - Use Ollama (local) or Groq (cloud)
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434/v1
GROQ_API_KEY=your-groq-api-key  # Fallback if Ollama unavailable
```

### Start Backend API Server

```powershell
# From project root
python backend_server.py
```

Backend will run on `http://localhost:8000`

Check health: http://localhost:8000/health

## Step 3: Frontend Setup

### Install Frontend Dependencies

```powershell
# Navigate to frontend
cd landing-page

# Install dependencies (already done)
npm install
```

### Configure Frontend Environment

```powershell
# Copy example env file
Copy-Item .env.local.example .env.local

# Edit .env.local
notepad .env.local
```

Fill in these values in `.env.local`:

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Start Frontend Dev Server

```powershell
npm run dev
```

Frontend will run on `http://localhost:3000`

## Step 4: Start LiveKit Agent

In a **new terminal**, start the LiveKit agent that will handle voice interactions:

```powershell
cd C:\Users\vedan\Desktop\mcp-rag\voice-agent

# Start the agent (connects to your LiveKit server)
python livekit_mcp_agent.py start
```

## Step 5: Start LiveKit Server (if not running)

If you need to run LiveKit server locally:

```powershell
# Download and run LiveKit server
# See: https://docs.livekit.io/home/self-hosting/local/

# Or use Docker:
docker run --rm -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev
```

## Usage Flow

1. **Open Frontend**: Navigate to `http://localhost:3000`
2. **Sign In**: Click "Sign in with Google" button
3. **View Credits**: See your 10 free credits displayed
4. **Start Session**: Click "Start Voice Session" button (uses 1 credit)
5. **Talk**: Speak naturally to the AI assistant about Airbnb searches
6. **Continuous Chat**: The session remains active until you disconnect
7. **End Session**: Click "End Session" when done

## Testing

### Test Authentication

```powershell
# Test login endpoint
curl -X POST http://localhost:8000/auth/google `
  -H "Content-Type: application/json" `
  -d '{"token":"test-token"}'
```

### Test Backend Health

```powershell
curl http://localhost:8000/health
```

### Check Database

```powershell
# View users and credits
sqlite3 voiceplan.db "SELECT email, credits FROM users;"

# View usage logs
sqlite3 voiceplan.db "SELECT * FROM usage_logs;"
```

## Troubleshooting

### Frontend Issues

**Problem**: "Google OAuth not loading"
- **Solution**: Check `NEXT_PUBLIC_GOOGLE_CLIENT_ID` in `.env.local`
- Ensure Google OAuth is configured with correct origins

**Problem**: "Cannot connect to backend"
- **Solution**: Check `NEXT_PUBLIC_API_URL` points to `http://localhost:8000`
- Verify backend server is running

### Backend Issues

**Problem**: "Invalid Google token"
- **Solution**: Ensure `GOOGLE_CLIENT_ID` matches your OAuth client
- Check Google Cloud Console credentials

**Problem**: "LiveKit token generation failed"
- **Solution**: Verify `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are correct
- Ensure LiveKit server is running

### Agent Issues

**Problem**: "Agent not responding to voice"
- **Solution**: Check Deepgram API key is valid
- Verify Ollama is running (or Groq key is set)
- Check LiveKit agent is connected: `python livekit_mcp_agent.py start`

**Problem**: "No audio output"
- **Solution**: Verify Cartesia API key
- Check browser microphone permissions

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    picture TEXT,
    credits INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Usage Logs Table

```sql
CREATE TABLE usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    credits_used INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## API Endpoints

### Authentication

- `POST /auth/google` - Login with Google OAuth token
- `GET /auth/me` - Get current user info

### LiveKit

- `POST /livekit/token` - Generate LiveKit access token (requires auth)

### Credits

- `POST /credits/check` - Check remaining credits (requires auth)

### Health

- `GET /health` - Server health check

## File Structure

```
voice-agent/
├── backend_server.py          # FastAPI backend with auth & credits
├── backend_requirements.txt   # Backend dependencies
├── livekit_mcp_agent.py      # LiveKit voice agent (unchanged)
├── voiceplan.db              # SQLite database (auto-created)
├── .env                      # Backend config (create from .env.example)
├── .env.example              # Backend config template
└── landing-page/
    ├── app/
    │   ├── layout.tsx        # Updated with Providers
    │   ├── page.tsx          # Main page
    │   └── providers.tsx     # Auth & OAuth providers
    ├── components/
    │   └── voice-interaction.tsx  # Updated with LiveKit
    ├── contexts/
    │   └── auth-context.tsx  # Authentication context
    ├── .env.local            # Frontend config (create from example)
    └── .env.local.example    # Frontend config template
```

## Production Deployment

### Backend

1. Use PostgreSQL instead of SQLite
2. Set proper JWT secret
3. Configure CORS for production domain
4. Use environment variables, not .env file
5. Deploy to Heroku, Railway, or AWS

### Frontend

1. Update `NEXT_PUBLIC_API_URL` to production backend URL
2. Add production domain to Google OAuth origins
3. Deploy to Vercel, Netlify, or AWS Amplify

### LiveKit Agent

1. Deploy agent as a worker process
2. Use production LiveKit server
3. Ensure MCP Airbnb server is accessible

## Support

For issues:
1. Check logs in backend terminal
2. Check browser console for frontend errors
3. Verify all API keys are valid
4. Ensure all services are running (backend, frontend, agent, LiveKit server)

## Credits System

- Each Gmail account gets **10 free credits**
- Each voice session costs **1 credit**
- Credits are deducted when user clicks "Start Voice Session"
- To reset credits for testing: `sqlite3 voiceplan.db "UPDATE users SET credits = 10;"`
