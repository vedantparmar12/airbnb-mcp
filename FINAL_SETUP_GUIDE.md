# 🎯 Final Setup Guide - LiveKit Voice Agent (100% Ready)

## ✅ What You Have (All FREE except Deepgram STT)

| Component | Provider | Cost | Configured |
|-----------|----------|------|------------|
| **LLM** | Ollama `gpt-oss:20b-cloud` | ✅ FREE | ✅ Yes |
| **TTS** | Cartesia | ✅ FREE tier | ✅ Yes |
| **STT** | Deepgram | 💰 Paid | ✅ Yes |
| **MCP** | Your Airbnb Server (stdio) | ✅ FREE | ✅ Yes |

## 🚀 Quick Start (3 Steps)

### Step 1: Verify Ollama is Running

```bash
# Start Ollama (if not running)
ollama serve

# Verify your model is available
ollama list
# Should see: gpt-oss:20b-cloud
```

**If model not found:**
```bash
ollama pull gpt-oss:20b-cloud
```

### Step 2: Verify Configuration

Your `.env` file is already configured:
```bash
✅ OLLAMA_MODEL=gpt-oss:20b-cloud
✅ OLLAMA_BASE_URL=http://localhost:11434/v1
✅ CARTESIA_API_KEY=sk_car_EcFsUx7YWyVcXnjpAqhuq7
✅ DEEPGRAM_API_KEY=964d569f4c6b8fb8398e9619d1aff16e448dfafa
✅ LIVEKIT_URL=wss://airbnb-voice-agent-4ahy6tsh.livekit.cloud
```

**Everything is set! ✅**

### Step 3: Run the Agent

```bash
# Navigate to voice-agent directory
cd C:\Users\vedan\Desktop\mcp-rag\voice-agent

# Run in console mode (for testing)
python livekit_mcp_agent.py console
```

**Expected output:**
```
🚀 Starting LiveKit Agent with MCP Airbnb Server + Ollama...
✅ Agent running with MCP tools + Ollama
Livekit Agents - Console
Press [Ctrl+B] to toggle between Text/Audio mode, [Q] to quit.
```

## 🎤 Test Voice Commands

Once running, try:

```
"Search for Airbnbs in Goa"
"Find me places in Mumbai"
"Get details for listing 123456"
"Compare prices for different dates"
"Calculate budget for this trip"
```

## 📋 What Happens Under the Hood

```
Your Voice
    ↓
Deepgram STT (voice → text)
    ↓
Ollama gpt-oss:20b-cloud (understand + decide which tool)
    ↓
MCP Airbnb Server (spawned automatically via stdio)
    ├─ airbnb_search
    ├─ airbnb_listing_details
    ├─ airbnb_price_analyzer
    ├─ airbnb_trip_budget
    ├─ airbnb_smart_filter
    └─ airbnb_compare_listings
    ↓
Ollama gpt-oss:20b-cloud (format response)
    ↓
Cartesia TTS (text → voice)
    ↓
Your Speakers
```

## 🔧 Configuration Breakdown

### Your `.env` File (Already Configured)

```bash
# 1. Ollama LLM (FREE)
OLLAMA_MODEL=gpt-oss:20b-cloud        # Your chosen model (fast!)
OLLAMA_BASE_URL=http://localhost:11434/v1

# 2. Cartesia TTS (FREE tier)
CARTESIA_API_KEY=sk_car_EcFsUx7YWyVcXnjpAqhuq7

# 3. Deepgram STT (Paid - you have it)
DEEPGRAM_API_KEY=964d569f4c6b8fb8398e9619d1aff16e448dfafa

# 4. LiveKit Cloud
LIVEKIT_URL=wss://airbnb-voice-agent-4ahy6tsh.livekit.cloud
LIVEKIT_API_KEY=APIp97jfqK6ZgH4
LIVEKIT_API_SECRET=ahNTGDu4FJfEqj9MOelmJxVWSyc4pW0bn8R6AjUe5M7B
```

### Your `livekit_mcp_agent.py` (Already Configured)

```python
# LLM - Reads OLLAMA_MODEL from .env
llm=openai.LLM.with_ollama(
    model=os.getenv("OLLAMA_MODEL", "deepseek-coder"),  # Will use gpt-oss:20b-cloud
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    temperature=0.7,
)

# TTS - Reads CARTESIA_API_KEY from .env
tts=cartesia.TTS(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",
    speed=1.0,
)

# MCP Server - Uses stdio (spawns per session)
mcp_servers=[
    mcp.MCPServerStdio(
        command="uv",
        args=[
            "--directory",
            r"C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb",
            "run",
            "python",
            "server.py"
        ]
    )
]
```

## ✅ Pre-Flight Checklist

Before running, verify:

```bash
# 1. Ollama is running
ollama serve
curl http://localhost:11434/api/version
# Should return: {"version":"0.x.x"}

# 2. Model is available
ollama list | grep gpt-oss
# Should show: gpt-oss:20b-cloud

# 3. UV is installed (for MCP)
uv --version

# 4. Python packages installed
pip list | grep livekit
# Should show: livekit-agents, livekit-plugins-openai, etc.
```

## 🎮 Run Modes

### 1. Console Mode (Recommended for Testing)

```bash
python livekit_mcp_agent.py console
```

**Features:**
- ✅ Text input/output
- ✅ Simulated voice pipeline
- ✅ Fast testing
- ✅ See all logs

### 2. Development Mode (LiveKit Cloud)

```bash
python livekit_mcp_agent.py dev
```

**Features:**
- ✅ Real voice calls
- ✅ Connects to LiveKit Cloud
- ✅ Production-like environment
- ✅ Multiple users can join

### 3. Connect to Room

```bash
python livekit_mcp_agent.py connect --room my-test-room
```

## 🐛 Troubleshooting

### Issue: Model not found

```bash
# Pull the model
ollama pull gpt-oss:20b-cloud

# Verify
ollama list | grep gpt-oss
```

### Issue: Ollama connection failed

```bash
# Start Ollama
ollama serve

# Test connection
curl http://localhost:11434/api/version
```

### Issue: MCP server fails to start

```bash
# Test MCP manually
cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
uv run python server.py

# Should see: "Starting Airbnb MCP Server"
# Press Ctrl+C to stop
```

### Issue: UV not found

```bash
# Install UV
pip install uv

# Or use pipx
pipx install uv
```

### Issue: Cartesia API key invalid

```bash
# Get new key from: https://play.cartesia.ai/
# Update in .env:
CARTESIA_API_KEY=sk_car_your_new_key
```

## 📊 Expected Behavior

### When You Run the Agent:

```
2025-10-05 18:00:00 - INFO - Agent started in room: console
2025-10-05 18:00:01 - INFO - Agent session started
2025-10-05 18:00:02 - INFO - 6 tools available: search, details, price_analyzer, trip_budget, smart_filter, compare_listings

==================================================
     Livekit Agents - Console
==================================================
Press [Ctrl+B] to toggle between Text/Audio mode, [Q] to quit.

You: Find Airbnbs in Goa

[Thinking with gpt-oss:20b-cloud...]
[Calling tool: airbnb_search(location="Goa")]
[Tool returned: Found 10 listings...]

Agent: I found 10 great Airbnbs in Goa! Let me tell you about the top ones...
```

## 🎯 Success Indicators

✅ You'll know it's working when you see:

1. **"6 tools available"** in logs
2. **"Agent session started"**
3. **Tool calls** like "airbnb_search(location='Goa')"
4. **Natural responses** from the agent

## 🚀 You're Ready!

**Everything is configured. Just run:**

```bash
python livekit_mcp_agent.py console
```

**Then say:** *"Find me Airbnbs in Goa!"* 🎙️

---

## 🔄 Next Steps (After Testing)

### Deploy to LiveKit Cloud

```bash
# Create livekit.toml (if not exists)
# Then deploy
lk agent deploy
```

### Customize

- **Change voice:** Edit `voice` in TTS config
- **Adjust speed:** Change `speed` in TTS config
- **Switch model:** Update `OLLAMA_MODEL` in `.env`
- **Add tools:** Modify MCP server tools

### Monitor

- **Check logs:** Terminal output
- **MCP logs:** Spawned with each session
- **Ollama logs:** `ollama logs`
- **LiveKit dashboard:** https://cloud.livekit.io

---

## 📝 Summary

**Your Setup:**
- ✅ Free LLM: Ollama `gpt-oss:20b-cloud` (you found it fast!)
- ✅ Free TTS: Cartesia (free tier)
- ✅ Paid STT: Deepgram (you have it)
- ✅ Free MCP: Your Airbnb server with 6 tools
- ✅ All configured via `.env` file
- ✅ Ready to run!

**One command to rule them all:**

```bash
python livekit_mcp_agent.py console
```

🎉 **Enjoy your voice-powered Airbnb assistant!** 🎉
