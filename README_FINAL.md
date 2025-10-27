# 🎙️ LiveKit Voice Agent with MCP Airbnb + Ollama

**Complete voice AI assistant for Airbnb search using local models (Ollama) + MCP tools**

## 🚀 Quick Start (3 Commands)

```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Check your API keys in .env file
# CARTESIA_API_KEY=sk_car_...
# DEEPGRAM_API_KEY=...

# 3. Run the agent!
python livekit_mcp_agent.py console
```

**Then say:** *"Find me Airbnbs in Goa"* 🎤

## 📋 What You Have

| Component | Provider | Cost | Purpose |
|-----------|----------|------|---------|
| **LLM** | Ollama (deepseek-coder) | ✅ FREE | Language understanding |
| **TTS** | Cartesia | ✅ FREE tier | Voice output |
| **STT** | Deepgram | 💰 Paid | Voice input |
| **MCP Server** | Your Airbnb server | ✅ FREE | 6 Airbnb tools |

## 🛠️ Available Airbnb Tools

Your agent has access to:

1. **airbnb_search** - Search for listings by location
2. **airbnb_listing_details** - Get detailed property info
3. **airbnb_price_analyzer** - Compare prices across dates
4. **airbnb_trip_budget** - Calculate total trip cost
5. **airbnb_smart_filter** - Advanced filtering & sorting
6. **airbnb_compare_listings** - Side-by-side comparison

## 🎯 Architecture

```
User Voice → Deepgram STT → Ollama LLM → MCP Tools → Ollama LLM → Cartesia TTS → User Voice
                                ↓
                         [Airbnb MCP Server]
                         (spawned per session)
```

## 📁 Project Structure

```
voice-agent/
├── livekit_mcp_agent.py      # Main agent (MCP + Ollama)
├── livekit_basic_agent.py    # Basic agent (no MCP, mock data)
├── .env                       # Configuration
├── SETUP_MCP_STDIO.md        # Detailed setup guide
└── README_FINAL.md           # This file

travel-agent-system/airbnb/mcp-server-airbnb/
├── server.py                 # MCP server (stdio)
├── server_fastapi.py         # HTTP API (for testing)
└── tools/                    # 6 Airbnb tools
```

## 🔑 Configuration (.env)

```bash
# Ollama (FREE - Local)
OLLAMA_MODEL=deepseek-coder
OLLAMA_BASE_URL=http://localhost:11434/v1

# Cartesia TTS (FREE tier)
CARTESIA_API_KEY=sk_car_your_key_here

# Deepgram STT
DEEPGRAM_API_KEY=your_key_here

# LiveKit Cloud
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_secret
```

## 🎤 Voice Commands Examples

```
"Find Airbnbs in Goa"
"Search for places in Mumbai for 2 adults"
"Get details for listing ABC123"
"Compare prices for next week vs next month"
"Calculate total budget for 3 nights"
"Show only 5-star rated places"
"Compare these three listings"
```

## 🔄 Different Run Modes

### 1. Console Mode (Testing)
```bash
python livekit_mcp_agent.py console
```
- Text + simulated voice
- Perfect for testing
- Fast iteration

### 2. Development Mode (LiveKit Cloud)
```bash
python livekit_mcp_agent.py dev
```
- Connects to LiveKit Cloud
- Real voice calls
- Production-like environment

### 3. Basic Agent (No MCP)
```bash
python livekit_basic_agent.py console
```
- Uses mock Airbnb data
- No MCP server needed
- Good for testing voice pipeline only

## ⚡ Performance Tips

### Faster Responses

```bash
# Use faster Ollama model
ollama pull phi3.5
# Update .env: OLLAMA_MODEL=phi3.5

# Or smaller model
ollama pull llama3.2:1b
# Update .env: OLLAMA_MODEL=llama3.2:1b
```

### Adjust Voice Speed

Edit `livekit_mcp_agent.py`:
```python
tts=cartesia.TTS(
    speed=1.2,  # Faster: 1.0-2.0
)
```

## 🐛 Troubleshooting

### Agent won't start

```bash
# Check Ollama
ollama serve
ollama list

# Check UV (for MCP)
uv --version

# Test MCP manually
cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
uv run python server.py
```

### MCP tools not working

```bash
# Check logs for "6 tools available"
python livekit_mcp_agent.py console
# Look for: "6 tools available: ..."

# Test with direct command
# Say: "Use airbnb_search to find listings in Goa"
```

### Slow responses

```bash
# Switch to faster model
ollama pull phi3.5
# Update OLLAMA_MODEL in .env
```

## 📊 Status Check Commands

```bash
# 1. Ollama
ollama list
curl http://localhost:11434/api/version

# 2. UV
uv --version

# 3. Python packages
pip list | grep livekit

# 4. Run agent
python livekit_mcp_agent.py console
```

## 🌟 Key Features

- ✅ **100% Local LLM** (Ollama - no OpenAI costs)
- ✅ **Real Airbnb Data** (via MCP tools)
- ✅ **Isolated Sessions** (stdio MCP per voice call)
- ✅ **Production Ready** (LiveKit Cloud deployment)
- ✅ **Easy Testing** (console mode)
- ✅ **Works with Claude Desktop** (same MCP server)

## 📚 Documentation

- **Detailed Setup:** `SETUP_MCP_STDIO.md`
- **LiveKit Docs:** https://docs.livekit.io/agents/
- **MCP Docs:** https://modelcontextprotocol.io/
- **Ollama Models:** https://ollama.com/library

## 🎓 How It Works

1. **User speaks** → Deepgram converts to text
2. **Text processed** → Ollama LLM understands intent
3. **Tool needed?** → Spawns MCP server, calls Airbnb tool
4. **Gets results** → MCP returns data
5. **Generates response** → Ollama creates natural reply
6. **Speaks back** → Cartesia converts to voice
7. **Session ends** → MCP server auto-terminates

## 🚢 Deploy to Production

```bash
# 1. Configure livekit.toml
# 2. Set environment variables in LiveKit Cloud
# 3. Deploy
lk agent deploy
```

See `SETUP_MCP_STDIO.md` for details.

## 💡 Tips

1. **Keep Ollama running** in background for faster startup
2. **Test in console mode** before deploying
3. **Monitor logs** for errors and tool calls
4. **Use faster models** (phi3.5) for production
5. **Check .env** if things don't work

## 🎉 Success Indicators

When everything works, you'll see:

```
✅ Agent session started
✅ 6 tools available: search, details, price_analyzer, ...
✅ User: "Find Airbnbs in Goa"
✅ Tool called: airbnb_search
✅ Agent: "I found 10 great listings..."
```

## 📞 Get Help

- **Setup issues:** Check `SETUP_MCP_STDIO.md`
- **Agent logs:** Look at terminal output
- **MCP issues:** Test `server.py` manually
- **Ollama issues:** Run `ollama serve` and check version

---

**Ready to test?**

```bash
python livekit_mcp_agent.py console
```

Say: *"Find me Airbnbs in Goa!"* 🎤✨
