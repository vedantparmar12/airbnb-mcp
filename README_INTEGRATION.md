# VoicePlan - LiveKit Voice Agent with Authentication

Complete integration connecting your Next.js frontend with `livekit_mcp_agent.py` backend, featuring Google OAuth and credit-based rate limiting.

## 🚀 Quick Start

### 1. Setup Environment Variables

```powershell
# Backend (.env)
Copy-Item .env.example .env
# Edit .env with your API keys

# Frontend (landing-page/.env.local)
cd landing-page
Copy-Item .env.local.example .env.local
# Edit .env.local with your Google Client ID
cd ..
```

### 2. Install Dependencies

```powershell
# Backend
pip install -r backend_requirements.txt

# Frontend (if not done)
cd landing-page
npm install
cd ..
```

### 3. Start All Services

**Option A: Use startup script (recommended)**
```powershell
.\start-all.ps1
```

**Option B: Manual start (3 separate terminals)**

Terminal 1 - Backend:
```powershell
python backend_server.py
```

Terminal 2 - Frontend:
```powershell
cd landing-page
npm run dev
```

Terminal 3 - LiveKit Agent:
```powershell
python livekit_mcp_agent.py start
```

### 4. Open and Use

1. Navigate to **http://localhost:3000**
2. Click **"Sign in with Google"**
3. You'll get **10 free credits** (one per Gmail account)
4. Click **"Start Voice Session"** (uses 1 credit)
5. **Talk naturally** to your AI Airbnb assistant
6. Conversation is **continuous** until you disconnect

## 📋 What Changed

### Frontend (`landing-page/`)
- ✅ **Added authentication** with Google OAuth
- ✅ **Replaced Web Speech API** with LiveKit client
- ✅ **Added credit display** showing remaining sessions
- ✅ **Protected microphone button** behind login
- ✅ **Continuous voice chat** using `livekit_mcp_agent.py`

### Backend (New Files)
- ✅ **backend_server.py** - FastAPI server with:
  - Google OAuth authentication
  - SQLite database for users and credits
  - LiveKit token generation
  - Rate limiting (10 credits per Gmail)
- ✅ **backend_requirements.txt** - Python dependencies

### Configuration Files
- ✅ `.env.example` - Backend config template
- ✅ `landing-page/.env.local.example` - Frontend config template
- ✅ `SETUP_GUIDE.md` - Detailed setup instructions
- ✅ `start-all.ps1` - Automated startup script

## 🔑 Required API Keys

Get these before starting:

1. **Google OAuth Client ID**
   - https://console.cloud.google.com/
   - Create OAuth 2.0 credentials
   - Add `http://localhost:3000` to authorized origins

2. **LiveKit Server** (API Key + Secret)
   - Run locally: `docker run --rm -p 7880:7880 -p 7881:7881 livekit/livekit-server --dev`
   - Or use LiveKit Cloud: https://cloud.livekit.io/

3. **Deepgram API Key** (Speech-to-Text)
   - https://deepgram.com/

4. **Cartesia API Key** (Text-to-Speech)
   - https://cartesia.ai/

5. **LLM** (Choose one):
   - **Ollama** (Local, FREE): Install from https://ollama.ai/
   - **Groq API Key** (Cloud, fallback): https://console.groq.com/

## 🏗️ Architecture

```
User Browser (localhost:3000)
    ↓ [Google OAuth Login]
    ↓
Backend API (localhost:8000)
    ↓ [Generate LiveKit Token]
    ↓ [Deduct 1 Credit]
    ↓
LiveKit Room
    ↓ [Voice Stream]
    ↓
livekit_mcp_agent.py
    ↓ [Deepgram STT]
    ↓ [Ollama/Groq LLM]
    ↓ [MCP Airbnb Tools]
    ↓ [Cartesia TTS]
    ↓
User hears AI response
```

## 💾 Database (SQLite)

Auto-created as `voiceplan.db` with:

**Users Table:**
- `email` - Gmail address (unique)
- `name` - Display name
- `credits` - Remaining sessions (default: 10)
- `created_at` - Account creation timestamp

**Usage Logs Table:**
- `user_id` - Foreign key to users
- `room_name` - LiveKit room identifier
- `started_at` - Session start time
- `credits_used` - Credits consumed (1 per session)

## 🔍 Testing

Check backend health:
```powershell
curl http://localhost:8000/health
```

View database:
```powershell
sqlite3 voiceplan.db "SELECT email, credits FROM users;"
```

Reset credits (for testing):
```powershell
sqlite3 voiceplan.db "UPDATE users SET credits = 10;"
```

## 📚 Documentation

- **SETUP_GUIDE.md** - Comprehensive setup instructions
- **backend_server.py** - Well-commented backend code
- **livekit_mcp_agent.py** - Original LiveKit agent (unchanged)

## 🐛 Troubleshooting

**"Login failed"**
→ Check `GOOGLE_CLIENT_ID` matches in both `.env` and `.env.local`

**"No credits remaining"**
→ Reset credits: `sqlite3 voiceplan.db "UPDATE users SET credits = 10;"`

**"Cannot connect to backend"**
→ Verify backend is running on port 8000

**"Agent not responding"**
→ Check all 3 services are running (backend, frontend, agent)
→ Verify LiveKit server is accessible

## 🎯 Features

✅ **Authenticated Sessions** - Only logged-in users can chat  
✅ **Credit System** - 10 free sessions per Gmail account  
✅ **Continuous Voice** - Talk as long as you want per session  
✅ **Real-time STT** - Deepgram speech recognition  
✅ **Natural TTS** - Cartesia voice synthesis  
✅ **Smart AI** - Ollama (local) or Groq (cloud) LLM  
✅ **Airbnb Tools** - Search, compare, analyze via MCP  
✅ **Usage Tracking** - SQLite logs all sessions  
✅ **Rate Limiting** - Credit-based access control  

## 📝 Next Steps

1. **Get API keys** (see Required API Keys section)
2. **Configure environment** (copy .env files)
3. **Run setup** (`.\start-all.ps1`)
4. **Test login** (use your Gmail)
5. **Start chatting!** (voice-powered Airbnb search)

For detailed instructions, see **SETUP_GUIDE.md**.
