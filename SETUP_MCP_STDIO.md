# LiveKit + MCP Airbnb (Stdio) Setup Guide

## 🎯 Architecture (RECOMMENDED)

```
┌─────────────────────────┐
│  LiveKit Voice Agent    │
│  (Ollama + Cartesia)    │
│                         │
│  For each session:      │
│  ├─ Spawns MCP process  │
│  ├─ Uses stdio pipes    │
│  └─ Auto cleanup        │
└─────────────────────────┘
           │ stdio
           ▼
    ┌──────────────┐
    │ MCP Instance │ (isolated per session)
    │ server.py    │
    │              │
    │ 6 tools      │
    └──────────────┘
```

## ✅ Why Stdio is CORRECT for LiveKit

### Stdio Benefits:
- ✅ **Isolated per session** - Each voice call gets fresh MCP instance
- ✅ **Automatic lifecycle** - Starts with session, ends with session
- ✅ **No concurrency issues** - No shared state between users
- ✅ **Production-ready** - Official LiveKit pattern
- ✅ **Works with Claude Desktop** - Can run both simultaneously
- ✅ **Clean & simple** - No HTTP server management needed

### Common Misconception:
> "HTTP is better for multiple clients"

**FALSE for LiveKit!** Each voice session SHOULD have isolated MCP instance. Stdio provides this automatically.

## 🚀 Quick Start

### Step 1: Check Prerequisites

```bash
# 1. Ollama is running
ollama serve

# 2. Check your model
ollama list
# Should see: deepseek-coder, llama3.2, or phi3.5

# 3. UV is installed (for MCP server)
uv --version
```

### Step 2: Configure Environment

Edit `.env`:
```bash
# Ollama (FREE - Local)
OLLAMA_MODEL=deepseek-coder
OLLAMA_BASE_URL=http://localhost:11434/v1

# Cartesia TTS (FREE tier available)
CARTESIA_API_KEY=sk_car_your_key_here

# Deepgram STT (Required)
DEEPGRAM_API_KEY=your_deepgram_key_here

# LiveKit Cloud
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```

### Step 3: Run the Voice Agent

```bash
# Test in console mode (text + voice simulation)
python livekit_mcp_agent.py console

# Or run in dev mode (connects to LiveKit Cloud)
python livekit_mcp_agent.py dev
```

That's it! No separate MCP server to start! 🎉

## 📝 How It Works

### When you start the agent:

1. **LiveKit agent starts** listening for sessions
2. **User joins** voice call
3. **Agent automatically spawns** MCP server process via stdio
4. **MCP tools become available** to the agent
5. **User can interact** with Airbnb tools via voice
6. **User leaves** call
7. **MCP process auto-terminates** (clean!)

### Example Voice Flow:

```
User: "Hey, find me Airbnbs in Goa"

Agent (internally):
  1. Detects speech via Deepgram STT
  2. Processes with Ollama LLM
  3. LLM decides to call airbnb_search tool
  4. Calls MCP server via stdio
  5. Gets results back
  6. Generates response with Ollama
  7. Speaks via Cartesia TTS

Agent: "I found 10 great Airbnbs in Goa!
       The top one is a beachfront villa at ₹3,500 per night
       with a 4.9 rating..."
```

## 🧪 Testing

### Console Mode (Recommended for Testing)

```bash
python livekit_mcp_agent.py console
```

**Try these voice commands:**

```
"Search for Airbnbs in Mumbai"
"Find me a place in Goa for next weekend"
"Get details for listing ABC123"
"Compare prices for different dates"
"Calculate the total budget for 3 nights"
```

### Development Mode (LiveKit Cloud)

```bash
python livekit_mcp_agent.py dev
```

Then connect via:
- LiveKit Playground: https://cloud.livekit.io
- Your own web app using LiveKit SDK

## 🔧 Configuration Options

### Change Ollama Model

For faster responses:
```bash
# Pull a faster model
ollama pull phi3.5

# Update .env
OLLAMA_MODEL=phi3.5
```

### Adjust Voice Speed

In `livekit_mcp_agent.py`:
```python
tts=cartesia.TTS(
    api_key=os.getenv("CARTESIA_API_KEY"),
    voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",
    speed=1.2,  # Faster: 1.2, Slower: 0.8
),
```

### Change Voice

Cartesia voices:
- `f786b574-daa5-4673-aa0c-cbe3e8534c02` - Default (neutral)
- Get more from: https://play.cartesia.ai/

## 🐛 Troubleshooting

### Issue: "MCP server failed to start"

**Check:**
1. UV is installed: `uv --version`
2. MCP server runs manually:
   ```bash
   cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
   uv run python server.py
   ```
3. Path in agent is correct (check `livekit_mcp_agent.py` line 137)

### Issue: "Ollama connection failed"

**Solution:**
```bash
# Start Ollama
ollama serve

# Test connection
curl http://localhost:11434/api/version
```

### Issue: "Cartesia API key invalid"

**Solution:**
1. Get free API key: https://play.cartesia.ai/
2. Update `.env`: `CARTESIA_API_KEY=sk_car_...`

### Issue: Slow responses

**Options:**

1. **Use faster Ollama model:**
   ```bash
   ollama pull phi3.5
   # Update .env: OLLAMA_MODEL=phi3.5
   ```

2. **Reduce temperature** (more focused, less creative):
   ```python
   llm=openai.LLM.with_ollama(
       model=os.getenv("OLLAMA_MODEL", "deepseek-coder"),
       temperature=0.3,  # Lower = faster
   ),
   ```

### Issue: MCP tools not being called

**Debug:**
1. Check agent logs - should see "6 tools available"
2. Try direct command: "Use airbnb_search to find listings in Goa"
3. Check Ollama model supports function calling (phi3.5, llama3.2, deepseek-coder do)

## 📊 Component Status Check

```bash
# 1. Ollama
ollama list
curl http://localhost:11434/api/version

# 2. UV (for MCP)
uv --version

# 3. Test MCP server manually
cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
uv run python server.py
# (Ctrl+C to stop)

# 4. Run LiveKit agent
cd C:\Users\vedan\Desktop\mcp-rag\voice-agent
python livekit_mcp_agent.py console
```

## 🎤 Voice Commands Examples

### Search
- "Find Airbnbs in Goa"
- "Search for places in Mumbai for 2 people"
- "Show me listings in Delhi"

### Get Details
- "Get details for listing 123456"
- "Tell me more about that property"
- "What amenities does it have?"

### Price Analysis
- "Compare prices for next week versus next month"
- "What are the cheapest dates to visit?"
- "Analyze pricing trends for Goa"

### Budget Calculator
- "Calculate total cost for 3 nights"
- "How much will it cost for 5 people?"
- "Break down the budget for this listing"

### Smart Filters
- "Show only 5-star rated places"
- "Find listings under ₹5000 per night"
- "Filter by best value for money"

### Compare
- "Compare these three listings"
- "Which one has better reviews?"
- "What's the price difference?"

## 🔄 Development Workflow

```bash
# 1. Start agent in dev mode
python livekit_mcp_agent.py dev

# 2. Make changes to code
# (Edit livekit_mcp_agent.py)

# 3. Stop agent (Ctrl+C)

# 4. Restart
python livekit_mcp_agent.py dev
```

**Note:** MCP server restarts automatically with each session!

## 🌐 Using with Claude Desktop (Simultaneously!)

You can use **stdio MCP server** with both:
- ✅ Claude Desktop (your existing config)
- ✅ LiveKit Agent (stdio config)

They run **independently** - each spawns own MCP instance!

**Claude Desktop config stays the same:**
```json
{
  "mcpServers": {
    "airbnb": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\vedan\\Desktop\\mcp-rag\\travel-agent-system\\airbnb\\mcp-server-airbnb",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

## 🚢 Production Deployment

For production to LiveKit Cloud:

### 1. Update environment variables in LiveKit Cloud dashboard
### 2. Deploy agent:

```bash
lk agent deploy
```

### 3. Configure livekit.toml:

```toml
[agent]
job_type = "room"
worker_type = "agent"
entrypoint = "livekit_mcp_agent:entrypoint"

[agent.prewarm]
count = 1  # Keep warm instances

[agent.env]
# Add your API keys here
```

## 💡 Best Practices

1. **Model Selection**
   - Development: `deepseek-coder` (good at tools)
   - Production: `phi3.5` (faster)
   - Budget: `llama3.2:1b` (smallest)

2. **Error Handling**
   - Agent logs all errors to stderr
   - MCP server logs to separate process
   - Check both if issues occur

3. **Performance**
   - Keep Ollama running (faster startup)
   - Use prewarm for LiveKit (keeps agents ready)
   - Monitor token usage in Ollama logs

4. **Testing**
   - Always test in console mode first
   - Then test in dev mode
   - Finally deploy to production

## 📚 Architecture Details

### Why Stdio Works Better Than HTTP

| Aspect | Stdio | HTTP |
|--------|-------|------|
| **Isolation** | ✅ Per session | ❌ Shared |
| **Lifecycle** | ✅ Automatic | ❌ Manual |
| **Concurrency** | ✅ No issues | ⚠️ Needs locks |
| **Complexity** | ✅ Simple | ❌ Complex |
| **Production** | ✅ Ready | ⚠️ Needs work |
| **Debugging** | ⚠️ Separate logs | ✅ Central |

### Component Stack

```
Voice Input (User Microphone)
    ↓
Deepgram STT (Speech → Text)
    ↓
Ollama LLM (Text → Intent + Tool Calls)
    ↓
MCP Stdio (Tool Execution)
    ↓
Ollama LLM (Results → Response)
    ↓
Cartesia TTS (Text → Speech)
    ↓
Voice Output (User Speaker)
```

## 🎯 Summary

**Current Setup:**
- ✅ Ollama for LLM (FREE, local, fast)
- ✅ Cartesia for TTS (FREE tier)
- ✅ Deepgram for STT (paid, but you have it)
- ✅ MCP via stdio (PERFECT for LiveKit)
- ✅ 6 Airbnb tools available

**To Run:**
```bash
# Just one command!
python livekit_mcp_agent.py console
```

**That's it!** The agent handles everything else automatically. 🎉

---

**Questions?** Check the logs:
- Agent logs: Terminal output
- MCP logs: Spawned with agent (check for "6 tools available")
- Ollama logs: `ollama logs` command
