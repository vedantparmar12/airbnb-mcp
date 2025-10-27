# 🚀 LiveKit Cloud Deployment Guide

## ✅ Prerequisites (Already Done)
- [x] LiveKit CLI installed
- [x] Authenticated with `lk cloud auth`
- [x] Default project set to `airbnb-voice-agent`
- [x] livekit.toml configured
- [x] Dockerfile ready

## 📋 Deployment Steps

### Step 1: Create Agent (One-time setup)

Run this command in your terminal:

```bash
lk agent create
```

**When prompted:**
- Select: `airbnb-voice-agent`
- Confirm agent creation

This will:
- Register your agent with LiveKit Cloud
- Add agent ID to `livekit.toml`
- Create initial deployment

### Step 2: Set Environment Variables

After agent is created, set your API keys as secrets in LiveKit Cloud:

```bash
# Cartesia TTS API Key (Required)
lk agent set-var CARTESIA_API_KEY ""

# Deepgram STT API Key (Required)
lk agent set-var DEEPGRAM_API_KEY ""

# Groq LLM API Key (Required - Production LLM)
lk agent set-var GROQ_API_KEY ""

# LiveKit credentials (auto-configured, but can override)
lk agent set-var LIVEKIT_URL ""
lk agent set-var LIVEKIT_API_KEY ""
lk agent set-var LIVEKIT_API_SECRET ""

# Optional: LLM Configuration
lk agent set-var LLM_CHOICE ""

# NOTE: Don't set OLLAMA variables for cloud deployment
# Cloud deployment will use Groq as LLM (Ollama only works locally)
```

**Alternative: Set via Dashboard**

You can also set environment variables in the LiveKit Cloud dashboard:
1. Go to https://cloud.livekit.io/projects/p_/agents
2. Select your agent
3. Click "Environment Variables"
4. Add each key-value pair

### Step 3: Deploy Agent

After setting environment variables, deploy your agent:

```bash
lk agent deploy
```

This will:
1. Upload your code
2. Build Docker image
3. Deploy to LiveKit Cloud
4. Start serving requests

**Expected output:**
```
✓ Uploading code...
✓ Building image...
✓ Deploying agent...
✓ Agent deployed successfully!
```

### Step 4: Monitor Status

Check agent status:

```bash
lk agent status
```

View live logs:

```bash
lk agent logs
```

## 🔄 Updating Your Agent

When you make code changes, redeploy with:

```bash
lk agent deploy
```

This does a rolling deployment:
- New instances get your updated code
- Old instances gracefully shutdown (1 hour for active sessions)
- Zero downtime

## 🎯 Testing Your Deployed Agent

### Option 1: Agent Playground
1. Go to https://cloud.livekit.io/projects/p_/agents/playground
2. Connect to your agent
3. Test voice interaction

### Option 2: Custom Frontend
Use the LiveKit web SDK to connect to your agent:

```javascript
const room = new Room();
await room.connect('', token);
```

### Option 3: Console Test (Local + Cloud)
```bash
python livekit_mcp_agent.py dev
```

## 🔧 Troubleshooting

### Agent not starting
```bash
# Check logs for errors
lk agent logs

# Check status
lk agent status

# Common issues:
# - Missing environment variables
# - Dockerfile build errors
# - API key issues
```

### Environment variable issues
```bash
# List all variables
lk agent list-vars

# Update a variable
lk agent set-var KEY "new_value"

# Delete a variable
lk agent delete-var KEY
```

### Build failures
```bash
# Check build logs
lk agent logs --build

# Common issues:
# - Missing dependencies in pyproject.toml
# - Dockerfile errors
# - UV sync issues
```

### MCP Tools not working
- MCP server is included in Docker image
- Check that `mcp-server-airbnb/` directory is copied
- Verify UV is installing MCP dependencies
- Check logs for MCP startup messages

## 📊 Important Notes

### Production LLM Configuration

**Cloud deployment uses GROQ, not Ollama:**
- Ollama runs locally only (requires localhost:11434)
- Cloud deployment automatically falls back to Groq
- Agent detects environment and chooses appropriate LLM

### API Costs

| Service | Tier | Cost |
|---------|------|------|
| **Cartesia TTS** | Free tier | 1M chars/month free |
| **Deepgram STT** | Pay-as-you-go | ~$0.0125/min |
| **Groq LLM** | Free tier | 30 req/min free |
| **LiveKit Cloud** | Free tier | 5k mins/month |

### Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use `lk agent set-var`** - Secrets are encrypted at rest
3. **Rotate API keys** - If exposed, rotate immediately
4. **Set file permissions** - Fix config file permissions:
   ```bash
   # On Windows (PowerShell as Admin)
   icacls "C:\Users\vedan\.livekit\cli-config.yaml" /inheritance:r /grant:r "$env:USERNAME:(R,W)"
   ```

## 🎉 Success Indicators

When deployment succeeds, you'll see:

```bash
$ lk agent status
Agent ID: ag_xxxxx
Status: Running
Replicas: 1/1
Last Deploy: 2 minutes ago
Version: v1
```

In the logs (`lk agent logs`):
```
✓ Agent session started
✓ 6 tools available: search, details, price_analyzer, ...
✓ Using Groq cloud LLM
✓ Cartesia TTS initialized
✓ Deepgram STT ready
```

## 📚 Additional Resources

- **LiveKit Agents Docs**: https://docs.livekit.io/agents/
- **LiveKit Cloud Dashboard**: https://cloud.livekit.io
- **MCP Documentation**: https://modelcontextprotocol.io
- **Groq API**: https://console.groq.com
- **Cartesia TTS**: https://play.cartesia.ai
- **Deepgram STT**: https://console.deepgram.com

## 🆘 Support

- **LiveKit Discord**: https://livekit.io/discord
- **GitHub Issues**: Your project repository
- **Documentation**: https://docs.livekit.io

---

## Quick Commands Cheat Sheet

```bash
# Deploy/Update
lk agent deploy

# Monitor
lk agent status
lk agent logs

# Environment Variables
lk agent set-var KEY "value"
lk agent list-vars
lk agent delete-var KEY

# Rollback (Paid plans only)
lk agent rollback

# Project Management
lk project list
lk project set-default "project-name"

# Testing
python livekit_mcp_agent.py dev
```
# Check it
"https://agents-playground.livekit.io/?cam=1&mic=1&screen=1&video=1&audio=1&chat=1&theme_color=green"