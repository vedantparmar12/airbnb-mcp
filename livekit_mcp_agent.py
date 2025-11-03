from dotenv import load_dotenv
from livekit import rtc
from livekit import agents
from livekit.agents import (
    NOT_GIVEN,
    Agent,
    AgentFalseInterruptionEvent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    ModelSettings,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
    mcp
)
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero, cartesia
from datetime import datetime
import logging
import os
import httpx
import re
# uncomment to enable Krisp background voice/noise cancellation
from livekit.plugins import noise_cancellation
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_text_for_voice(text: str) -> str:

    # Remove markdown tables (lines with multiple pipes)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.count('|') >= 2 or re.match(r'^[\s\-|:]+$', line):
            continue
        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Remove remaining pipes
    text = text.replace('|', '')

    # Remove markdown bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*(.+?)\*', r'\1', text)      # *italic*
    text = re.sub(r'__(.+?)__', r'\1', text)      # __bold__
    text = re.sub(r'_(.+?)_', r'\1', text)        # _italic_

    # Remove markdown bullets
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)

    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    return text.strip()


async def get_llm_instance():
    """
    Get LLM instance - tries Ollama first, falls back to Groq.
    Returns configured LLM instance.
    """
    ollama_model = os.getenv("OLLAMA_MODEL")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    groq_api_key = os.getenv("GROQ_API_KEY")

    # Try Ollama first if configured
    if ollama_model and ollama_base_url:
        try:
            logger.info(f"Attempting to use Ollama model: {ollama_model} at {ollama_base_url}")

            # Test if Ollama is reachable
            async with httpx.AsyncClient(timeout=5.0) as client:
                health_url = ollama_base_url.replace("/v1", "") + "/api/tags"
                response = await client.get(health_url)
                response.raise_for_status()

            logger.info("✓ Ollama is available - using local model")
            return openai.LLM.with_ollama(
                model=ollama_model,
                base_url=ollama_base_url,
                temperature=0.7,
            )

        except Exception as e:
            logger.warning(f"⚠ Ollama not available ({e}), falling back to Groq")

    # Fallback to Groq
    if groq_api_key:
        logger.info("Using Groq cloud LLM")
        return openai.LLM(
            model="llama-3.3-70b-versatile",
            base_url="https://api.groq.com/openai/v1",
            api_key=groq_api_key,
            temperature=0.7,
        )
    else:
        raise ValueError("No LLM configured - please set either OLLAMA_MODEL or GROQ_API_KEY in .env")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


class Assistant(Agent):
    
    def __init__(self):
        super().__init__(
            instructions="""You are a helpful and friendly Airbnb voice assistant.
            You can search for Airbnb listings, analyze prices, get detailed information,
            compare listings, and calculate trip budgets.

            You have access to these MCP tools:
            - airbnb_search: Search for listings in a location
            - airbnb_listing_details: Get detailed info about a specific listing
            - airbnb_price_analyzer: Compare prices across dates
            - airbnb_trip_budget: Calculate total trip cost
            - airbnb_smart_filter: Advanced search with filters
            - airbnb_compare_listings: Compare multiple listings side-by-side

            CRITICAL VOICE FORMATTING RULES:
            - This is a VOICE conversation, not text chat
            - NEVER use tables, pipes (|), asterisks, bullets, or special formatting
            - NEVER say "vertical bar", "pipe", "asterisk", or read punctuation
            - Speak in natural, flowing sentences as if talking to a friend
            - Example BAD: "Name vertical bar Cozy Loft vertical bar Price vertical bar 150"
            - Example GOOD: "The first option is Cozy Loft which costs 150 dollars per night"

            When presenting search results:
            - Say "I found X listings" then describe each one naturally
            - Example: "Option 1 is the Cozy Downtown Loft at 150 dollars per night with WiFi and kitchen"

            When comparing listings:
            - Describe differences in plain speech
            - Example: "The first listing is cheaper at 150 versus 200 for the second one"

            Speak clearly and naturally, as if having a phone conversation.
            Be concise but warm in your responses."""
        )
    
    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"The current date and time is {current_datetime}"       
    
    async def on_enter(self):
        """Called when the agent becomes active."""
        logger.info("Agent session started")

        # Set up text cleaning before TTS
        @self.session.on("agent_speech")
        def clean_speech_text(ev):
            """Clean formatting from agent speech before TTS"""
            if hasattr(ev, 'text') and ev.text:
                original = ev.text
                cleaned = clean_text_for_voice(ev.text)
                if original != cleaned:
                    logger.debug(f"Cleaned TTS text: {original[:50]}... -> {cleaned[:50]}...")
                    ev.text = cleaned

        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the user warmly and ask how you can help them find an Airbnb."
        )

    async def on_exit(self):
        """Called when the agent session ends."""
        logger.info("Agent session ended")


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the agent worker."""

    logger.info(f"Agent started in room: {ctx.room.name}")

    # Get LLM instance (tries Ollama first, falls back to Groq)
    llm_instance = await get_llm_instance()

    # Configure the voice pipeline
    session = AgentSession(
        # Speech-to-Text
        stt=deepgram.STT(
            model="nova-2",
            language="en",
            # Fix "vertical bar" hallucination issue
            interim_results=False,
            punctuate=True,
            smart_format=True,
        ),

        # Large Language Model - Ollama (local) or Groq (cloud)
        llm=llm_instance,

        # Text-to-Speech - Cartesia (Free Tier)
        tts=cartesia.TTS(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",
            speed=0.9,  # Slightly slower for smoother delivery
        ),
        
        # Voice Activity Detection - Improved sensitivity
        vad=silero.VAD.load(
            min_speech_duration=0.3,  # Minimum 300ms of speech
            min_silence_duration=0.5,  # Wait 500ms of silence before stopping
            padding_duration=0.2,     # Add 200ms padding
        ),

        # MCP servers - Your Airbnb server via Stdio (RECOMMENDED)
        # Each voice session gets isolated MCP instance - clean & production-ready
        mcp_servers=[
            mcp.MCPServerStdio(
                command="uv",
                args=[
                    "--directory",
                    os.path.join(os.path.dirname(__file__), "mcp-server-airbnb"),
                    "run",
                    "python",
                    "server.py"
                ]
            )
        ],
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        # room_input_options=RoomInputOptions(
            # Enable noise cancellation
            # noise_cancellation=noise_cancellation.BVC(),
            # For telephony, use: noise_cancellation.BVCTelephony()
        # ),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )
    
    # Handle session events
    @session.on("agent_state_changed")
    def on_state_changed(ev):
        """Log agent state changes."""
        logger.info(f"State: {ev.old_state} -> {ev.new_state}")
    
    @session.on("user_started_speaking")
    def on_user_speaking():
        """Track when user starts speaking."""
        logger.debug("User started speaking")
    
    @session.on("user_stopped_speaking")
    def on_user_stopped():
        """Track when user stops speaking."""
        logger.debug("User stopped speaking")


if __name__ == "__main__":
    # Run the agent using LiveKit CLI
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
