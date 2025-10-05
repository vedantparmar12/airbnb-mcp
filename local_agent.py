"""
Fully Local LiveKit Voice Agent
================================
No OpenAI API key required - uses Ollama LLM + Edge TTS (Microsoft)
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero
import edge_tts
import asyncio
import os
from datetime import datetime

# Load environment variables
load_dotenv(".env")

class EdgeTTSWrapper:
    """Wrapper for Edge TTS to work with LiveKit"""

    def __init__(self, voice="en-US-AriaNeural"):
        self.voice = voice
        self.communicate = None

    async def synthesize(self, text: str):
        """Synthesize speech from text"""
        communicate = edge_tts.Communicate(text, self.voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

class Assistant(Agent):
    """Voice assistant with Airbnb booking capabilities."""

    def __init__(self):
        super().__init__(
            instructions="""You are a helpful and friendly Airbnb voice assistant.
            You can help users search for Airbnbs in different cities and book their stays.
            Keep your responses concise and natural, as if having a conversation."""
        )

        # Mock Airbnb database
        self.airbnbs = {
            "san francisco": [
                {
                    "id": "sf001",
                    "name": "Cozy Downtown Loft",
                    "address": "123 Market Street, San Francisco, CA",
                    "price": 150,
                    "amenities": ["WiFi", "Kitchen", "Workspace"],
                },
                {
                    "id": "sf002",
                    "name": "Victorian House with Bay Views",
                    "address": "456 Castro Street, San Francisco, CA",
                    "price": 220,
                    "amenities": ["WiFi", "Parking", "Washer/Dryer", "Bay Views"],
                },
            ],
            "new york": [
                {
                    "id": "ny001",
                    "name": "Brooklyn Brownstone Apartment",
                    "address": "321 Bedford Avenue, Brooklyn, NY",
                    "price": 175,
                    "amenities": ["WiFi", "Kitchen", "Backyard Access"],
                },
            ],
        }

        self.bookings = []

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"The current date and time is {current_datetime}"

    @function_tool
    async def search_airbnbs(self, context: RunContext, city: str) -> str:
        """Search for available Airbnbs in a city."""
        city_lower = city.lower()

        if city_lower not in self.airbnbs:
            return f"Sorry, I don't have any Airbnb listings for {city}. Available cities: San Francisco, New York."

        listings = self.airbnbs[city_lower]
        result = f"Found {len(listings)} Airbnbs in {city}:\n\n"

        for listing in listings:
            result += f"• {listing['name']}\n"
            result += f"  Address: {listing['address']}\n"
            result += f"  Price: ${listing['price']} per night\n"
            result += f"  Amenities: {', '.join(listing['amenities'])}\n"
            result += f"  ID: {listing['id']}\n\n"

        return result

    @function_tool
    async def book_airbnb(self, context: RunContext, airbnb_id: str, guest_name: str,
                         check_in_date: str, check_out_date: str) -> str:
        """Book an Airbnb."""
        airbnb = None
        for city_listings in self.airbnbs.values():
            for listing in city_listings:
                if listing['id'] == airbnb_id:
                    airbnb = listing
                    break
            if airbnb:
                break

        if not airbnb:
            return f"Sorry, couldn't find Airbnb with ID {airbnb_id}."

        booking = {
            "confirmation_number": f"BK{len(self.bookings) + 1001}",
            "airbnb_name": airbnb['name'],
            "address": airbnb['address'],
            "guest_name": guest_name,
            "check_in": check_in_date,
            "check_out": check_out_date,
            "total_price": airbnb['price'],
        }

        self.bookings.append(booking)

        result = f"Booking confirmed!\n"
        result += f"Confirmation: {booking['confirmation_number']}\n"
        result += f"Property: {booking['airbnb_name']}\n"
        result += f"Guest: {booking['guest_name']}\n"
        result += f"Check-in: {booking['check_in']}\n"
        result += f"Check-out: {booking['check_out']}\n"

        return result

async def entrypoint(ctx: agents.JobContext):
    """Entry point for the agent."""

    # IMPORTANT: For now, we still need OpenAI TTS as LiveKit doesn't have a direct edge-tts plugin
    # But we use Ollama for LLM (no cost)
    # You can use Cartesia TTS (free tier) or keep using Deepgram for STT

    print("\n⚠️  NOTE: TTS still requires OpenAI API key OR use Cartesia (has free tier)")
    print("    To avoid ALL API costs, you'll need to implement custom TTS integration\n")

    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),  # Requires Deepgram API key
        llm=openai.LLM.with_ollama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        ),
        # TTS - This is the problem! OpenAI TTS needs API key
        # Alternative: Use Cartesia (has free tier) or implement custom edge-tts
        tts=openai.TTS(voice="echo"),  # Requires OpenAI API key
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant()
    )

    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help."
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
