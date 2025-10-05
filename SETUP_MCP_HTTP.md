# LiveKit + MCP Airbnb (HTTP) Setup Guide

## 🎯 Architecture

```
┌─────────────────────┐
│  LiveKit Agent      │
│  (Ollama + Cartesia)│
│                     │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│  MCP Airbnb Server  │
│  http://localhost:8089
│                     │
│  - airbnb_search    │
│  - listing_details  │
│  - price_analyzer   │
│  - trip_budget      │
│  - smart_filter     │
│  - compare_listings │
└─────────────────────┘
```

## ✅ Why HTTP instead of Stdio?

### Stdio Issues:
- ❌ LiveKit spawns new MCP server for each session
- ❌ Can't share with Claude Desktop simultaneously
- ❌ Hard to debug
- ❌ Not production-ready

### HTTP Benefits:
- ✅ One MCP server serves multiple clients
- ✅ Use with Claude Desktop + LiveKit simultaneously
- ✅ Easy to debug (see logs in one place)
- ✅ Production-ready
- ✅ Can run on different machines
- ✅ Better error handling

## 🚀 Quick Start

### Step 1: Start Ollama
```bash
ollama serve
```

### Step 2: Start MCP Airbnb HTTP Server
```bash
# Terminal 1
cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
python server_http.py
```

You should see:
```
🚀 Starting Airbnb MCP Server (HTTP)
📡 Running on http://localhost:8089
🔧 6 tools available: search, details, price_analyzer, trip_budget, smart_filter, compare_listings
```

### Step 3: Start LiveKit Voice Agent
```bash
# Terminal 2
cd C:\Users\vedan\Desktop\mcp-rag\voice-agent
python livekit_mcp_agent.py console
```

## 📝 Configuration

### .env file:
```bash
# Ollama (FREE)
OLLAMA_MODEL=deepseek-coder
OLLAMA_BASE_URL=http://localhost:11434/v1

# Cartesia TTS (FREE tier)
CARTESIA_API_KEY=sk_car_your_key_here

# Deepgram STT
DEEPGRAM_API_KEY=your_key_here

# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
```

## 🧪 Testing

### Test MCP Server (without LiveKit):
```bash
# Check if server is running
curl http://localhost:8089/sse
```

### Test with LiveKit Console:
```bash
python livekit_mcp_agent.py console
```

Then say:
- "Search for Airbnbs in Goa"
- "Find listings in New York for next weekend"
- "Compare prices for different dates"

## 🔧 Troubleshooting

### Issue: "Connection refused to localhost:8089"
**Solution:** Make sure MCP HTTP server is running first

```bash
cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
python server_http.py
```

### Issue: Ollama not responding
**Solution:** Check Ollama is running

```bash
ollama serve
ollama list  # Check models
```

### Issue: Slow responses
**Solution:** Use faster Ollama model

```bash
ollama pull phi3.5
# Update .env: OLLAMA_MODEL=phi3.5
```

### Issue: MCP tools not working
**Solution:** Check MCP server logs in Terminal 1

Look for:
- "6 tools available" message
- Any error messages when tools are called

## 📊 Components Status Check

| Component | Status | Port |
|-----------|--------|------|
| Ollama | `ollama list` | 11434 |
| MCP HTTP Server | `curl localhost:8089/sse` | 8089 |
| LiveKit Agent | `python livekit_mcp_agent.py console` | - |

## 🎤 Voice Commands Examples

**Search:**
- "Find me Airbnbs in Goa"
- "Search for places in Mumbai for 2 adults"

**Details:**
- "Get details for listing ABC123"
- "Tell me more about this property"

**Price Analysis:**
- "Compare prices for next week vs next month"
- "What are the cheapest dates to visit?"

**Budget:**
- "Calculate total budget for listing XYZ"
- "How much will it cost for 3 nights?"

**Filter:**
- "Show me only 5-star rated places"
- "Find places under 5000 rupees"

**Compare:**
- "Compare these three listings"
- "Which one has better amenities?"

## 🔄 Development Workflow

1. **Start MCP Server** (runs continuously)
2. **Make changes to agent code**
3. **Restart LiveKit agent** (MCP server keeps running)
4. **Test changes**

No need to restart MCP server unless you change tool implementations!

## 🌐 Using with Claude Desktop

You can use the **same MCP HTTP server** for both LiveKit and Claude Desktop!

Update Claude Desktop config:
```json
{
  "mcpServers": {
    "airbnb-http": {
      "url": "http://localhost:8089/sse"
    }
  }
}
```

## 🚢 Production Deployment

For production, deploy the MCP server to cloud:

1. **Deploy MCP Server**:
   - Fly.io, Railway, or any VPS
   - Use environment variables for configuration
   - Add authentication if needed

2. **Update LiveKit Agent**:
   ```python
   mcp_servers=[
       mcp.MCPServerHTTP(
           url="https://your-mcp-server.com/sse"
       )
   ]
   ```

3. **Scale**:
   - One MCP server can handle multiple LiveKit agents
   - Add rate limiting if needed
   - Monitor with logs/metrics

## ⚡ Performance Tips

1. **Use faster Ollama models**: phi3.5, qwen2.5:1.5b
2. **Run MCP server on same machine** for lowest latency
3. **Use connection pooling** if making many requests
4. **Cache frequent Airbnb searches** in MCP server

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [LiveKit Agents Docs](https://docs.livekit.io/agents/)
- [Ollama Models](https://ollama.com/library)

---

**Need Help?** Check logs in both terminals:
- **Terminal 1**: MCP server logs (tool calls, errors)
- **Terminal 2**: LiveKit agent logs (voice pipeline, state)
