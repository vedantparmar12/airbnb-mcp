# Testing Voice Agent Locally

## Prerequisites

Make sure you have these in your `.env` file:
```env
# Required for connecting to LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# Required for voice pipeline
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key

# Optional: Language (defaults to "multi" for auto-detection)
DEEPGRAM_LANGUAGE=multi

# LLM - Choose one:
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434/v1
# OR
GROQ_API_KEY=your-groq-key
```

## Option 1: Console Mode (Terminal Testing)

Test in your terminal with audio input/output:

```bash
uv run python livekit_mcp_agent.py console
```

This starts an interactive voice session in your terminal where you can speak and hear the agent respond.

## Option 2: Dev Mode (Browser Testing)

1. Start the agent in development mode:
```bash
uv run python livekit_mcp_agent.py dev
```

2. Open the provided URL in your browser (it will show something like):
```
Agent development mode started
Connect to: http://localhost:3000/?url=wss://...
```

3. Click "Connect" in the browser to start talking with the agent

## Option 3: Connect with Playground

1. Start the agent:
```bash
uv run python livekit_mcp_agent.py start
```

2. Go to LiveKit Cloud Playground: https://cloud.livekit.io/projects/your-project/playground

3. Join a room and the agent will automatically connect

## Testing the Features

Try these commands to test MCP Airbnb integration:
- "Search for Airbnbs in Paris"
- "Find me a 2 bedroom apartment in Tokyo for under 100 dollars"
- "Compare listings in New York"
- "Calculate the total cost for a 5 night stay"

## Troubleshooting

**Ollama not working?**
- Make sure Ollama is running: `ollama serve`
- Test: `ollama list` should show your model
- Fallback to Groq if needed

**No audio?**
- Check microphone permissions
- Verify DEEPGRAM_API_KEY and CARTESIA_API_KEY are set
- Try refreshing the browser

**MCP server not connecting?**
- Make sure `mcp-server-airbnb` folder exists
- Check that `server.py` is in the folder
- The agent will show MCP connection logs

## Speed/Language Adjustments

Current settings (in `livekit_mcp_agent.py`):
- **Voice speed**: `speed=0.7` (slower, clearer)
- **Language**: `language="multi"` (auto-detect) or set `DEEPGRAM_LANGUAGE` in `.env`
- **Noise cancellation**: Enabled with BVC (Background Voice Cancellation)

To change:
- Adjust `speed` parameter in TTS config (0.5-1.5)
- Set specific language: `DEEPGRAM_LANGUAGE=en` or `es`, `fr`, `hi`, etc.
