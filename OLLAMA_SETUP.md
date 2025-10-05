# Using Ollama with LiveKit Voice Agent

This guide shows you how to use Ollama (local LLM) instead of OpenAI for your LiveKit voice agent.

## ✅ Changes Made

The agent has been updated to use Ollama through LiveKit's OpenAI plugin:

```python
llm=openai.LLM.with_ollama(
    model=os.getenv("OLLAMA_MODEL", "llama3.1"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
)
```

## 📋 Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running locally

## 🚀 Setup Instructions

### Step 1: Install Ollama

**Windows:**
```bash
# Download from https://ollama.com/download/windows
# Or use winget:
winget install Ollama.Ollama
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Start Ollama Service

```bash
# Start Ollama server (runs on http://localhost:11434)
ollama serve
```

### Step 3: Pull a Model

Choose a model based on your needs:

**Recommended for voice agents:**
```bash
# Fast and efficient (4.7GB)
ollama pull llama3.1

# Better quality, slower (4.7GB)
ollama pull llama3.2

# Smaller, faster (2.0GB)
ollama pull phi3

# Very small, fastest (1.2GB)
ollama pull tinyllama
```

**Check available models:**
```bash
ollama list
```

### Step 4: Configure Environment Variables

Edit `.env` file:
```bash
# Ollama Configuration
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434/v1

# You still need Deepgram for speech-to-text
DEEPGRAM_API_KEY=your-deepgram-key
```

### Step 5: Run the Agent

```bash
# Using uv (recommended)
uv run python mcp_agent.py dev

# Or using python directly
python mcp_agent.py dev
```

## 🎯 Available Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.1 | 4.7GB | Medium | High | **Recommended** - Balanced |
| llama3.2 | 4.7GB | Medium | Very High | Quality conversations |
| phi3 | 2.0GB | Fast | Good | Faster responses |
| tinyllama | 1.2GB | Very Fast | Fair | Testing, low-end hardware |
| mistral | 4.1GB | Medium | High | Alternative to llama |
| qwen2.5 | 4.7GB | Medium | High | Multilingual support |

## ⚙️ Configuration Options

### Change Model at Runtime

```bash
# Set in environment
export OLLAMA_MODEL=phi3

# Or modify .env file
OLLAMA_MODEL=phi3
```

### Use Remote Ollama Server

```bash
# If Ollama is running on another machine
OLLAMA_BASE_URL=http://192.168.1.100:11434/v1
```

### Adjust Model Parameters

You can also adjust temperature for more/less creative responses:

```python
llm=openai.LLM.with_ollama(
    model="llama3.1",
    base_url="http://localhost:11434/v1",
    temperature=0.7,  # 0.0 = deterministic, 1.0 = creative
)
```

## 🔍 Troubleshooting

### Ollama Not Found

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Should return: {"version":"0.x.x"}
```

### Model Not Downloaded

```bash
# List installed models
ollama list

# Pull the model if missing
ollama pull llama3.1
```

### Connection Refused

```bash
# Make sure Ollama service is running
ollama serve

# On Windows, check if running as service:
Get-Service ollama
```

### Slow Response Times

- Use smaller models: `phi3` or `tinyllama`
- Ensure GPU support is enabled (NVIDIA/AMD)
- Increase system RAM allocation

### Port Already in Use

```bash
# Change Ollama port
OLLAMA_HOST=0.0.0.0:11435 ollama serve

# Update .env
OLLAMA_BASE_URL=http://localhost:11435/v1
```

## 📊 Performance Comparison

| Provider | Latency | Cost | Privacy | Quality |
|----------|---------|------|---------|---------|
| **Ollama** | Medium | **Free** | **100% Private** | Good-High |
| OpenAI | Low | Paid | Cloud | Very High |
| Anthropic | Low | Paid | Cloud | Very High |

## 🔄 Switching Back to OpenAI

To revert to OpenAI, change in your agent file:

```python
# From Ollama:
llm=openai.LLM.with_ollama(model="llama3.1", base_url="http://localhost:11434/v1")

# Back to OpenAI:
llm=openai.LLM(model="gpt-4.1-mini")
```

And set `OPENAI_API_KEY` in `.env`.

## 📚 Resources

- [Ollama Official Docs](https://ollama.com/)
- [Ollama Model Library](https://ollama.com/library)
- [LiveKit Ollama Integration](https://docs.livekit.io/agents/integrations/llm/ollama/)
- [Model Comparison](https://ollama.com/library?sort=popular)

## 💡 Tips

1. **Start with llama3.1** for best balance
2. **Use smaller models** during development for faster iteration
3. **Keep Ollama running** in background for instant responses
4. **Monitor memory usage** - models load into RAM
5. **Test locally first** before deploying to production

## 🎉 Next Steps

- Test the agent: `uv run python mcp_agent.py console`
- Try different models to find the best fit
- Adjust temperature for response style
- Monitor token usage and latency
