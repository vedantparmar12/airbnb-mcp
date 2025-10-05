"""
LiveKit Voice Agent - Quick Start
==================================
The simplest possible LiveKit voice agent to get you started.
Requires only OpenAI and Deepgram API keys.
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero, cartesia
from datetime import datetime
import os

# Load environment variables
load_dotenv(".env")

class Assistant(Agent):
    """Basic voice assistant with Airbnb booking capabilities."""

    def __init__(self):
        super().__init__(
            instructions="""You are a helpful and friendly Airbnb voice assistant.
            You can help users search for Airbnbs in different cities and book their stays.
            Keep your responses concise and natural, as if having a conversation.

            IMPORTANT: When describing listings, speak naturally in sentences.
            DO NOT use tables, pipe characters, or structured formatting.
            Just describe the properties conversationally."""
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
                {
                    "id": "sf003",
                    "name": "Modern Studio near Golden Gate",
                    "address": "789 Presidio Avenue, San Francisco, CA",
                    "price": 180,
                    "amenities": ["WiFi", "Kitchen", "Pet Friendly"],
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
                {
                    "id": "ny002",
                    "name": "Manhattan Skyline Penthouse",
                    "address": "555 Fifth Avenue, Manhattan, NY",
                    "price": 350,
                    "amenities": ["WiFi", "Gym", "Doorman", "City Views"],
                },
                {
                    "id": "ny003",
                    "name": "Artsy East Village Loft",
                    "address": "88 Avenue A, Manhattan, NY",
                    "price": 195,
                    "amenities": ["WiFi", "Washer/Dryer", "Exposed Brick"],
                },
            ],
            "los angeles": [
                {
                    "id": "la001",
                    "name": "Venice Beach Bungalow",
                    "address": "234 Ocean Front Walk, Venice, CA",
                    "price": 200,
                    "amenities": ["WiFi", "Beach Access", "Patio"],
                },
                {
                    "id": "la002",
                    "name": "Hollywood Hills Villa",
                    "address": "777 Mulholland Drive, Los Angeles, CA",
                    "price": 400,
                    "amenities": ["WiFi", "Pool", "City Views", "Hot Tub"],
                },
            ],
        }

        # Track bookings
        self.bookings = []

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"The current date and time is {current_datetime}"

    @function_tool
    async def search_airbnbs(self, context: RunContext, city: str) -> str:
        """Search for available Airbnbs in a city.

        Args:
            city: The city name to search for Airbnbs (e.g., 'San Francisco', 'New York', 'Los Angeles')
        """
        city_lower = city.lower()

        if city_lower not in self.airbnbs:
            return f"Sorry, I don't have any Airbnb listings for {city} at the moment. Available cities are: San Francisco, New York, and Los Angeles."

        listings = self.airbnbs[city_lower]
        result = f"I found {len(listings)} available Airbnbs in {city}. "

        for i, listing in enumerate(listings, 1):
            result += f"Option {i} is {listing['name']} located at {listing['address']}. "
            result += f"It costs ${listing['price']} per night and includes {', '.join(listing['amenities'])}. "
            result += f"The ID is {listing['id']}. "

        result += "Which one would you like to know more about or book?"
        return result

    @function_tool
    async def book_airbnb(self, context: RunContext, airbnb_id: str, guest_name: str, check_in_date: str, check_out_date: str) -> str:
        """Book an Airbnb.

        Args:
            airbnb_id: The ID of the Airbnb to book (e.g., 'sf001')
            guest_name: Name of the guest making the booking
            check_in_date: Check-in date (e.g., 'January 15, 2025')
            check_out_date: Check-out date (e.g., 'January 20, 2025')
        """
        # Find the Airbnb
        airbnb = None
        for city_listings in self.airbnbs.values():
            for listing in city_listings:
                if listing['id'] == airbnb_id:
                    airbnb = listing
                    break
            if airbnb:
                break

        if not airbnb:
            return f"Sorry, I couldn't find an Airbnb with ID {airbnb_id}. Please search for available listings first."

        # Create booking
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

        result = f"Great news! Your booking is confirmed. "
        result += f"Your confirmation number is {booking['confirmation_number']}. "
        result += f"You've booked {booking['airbnb_name']} located at {booking['address']}. "
        result += f"The reservation is for {booking['guest_name']} "
        result += f"from {booking['check_in']} to {booking['check_out']}. "
        result += f"The nightly rate is ${booking['total_price']}. "
        result += f"You'll receive a confirmation email shortly. Have a great stay!"

        return result        

async def entrypoint(ctx: agents.JobContext):
    """Entry point for the agent."""

    # Configure the voice pipeline with Ollama LLM + Cartesia TTS
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            language="en",
            # Fix "vertical bar" hallucination issue
            interim_results=False,
            punctuate=True,
            smart_format=True,
        ),
        llm=openai.LLM.with_ollama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        ),
        # Cartesia TTS (free tier available at https://play.cartesia.ai/)
        tts=cartesia.TTS(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",  # Default voice
            speed=0.9,  # Slightly slower for smoother delivery
        ),
        # Improve VAD sensitivity to reduce false positives
        vad=silero.VAD.load(
            min_speech_duration=0.3,  # Minimum 300ms of speech
            min_silence_duration=0.5,  # Wait 500ms of silence before stopping
            padding_duration=0.2,     # Add 200ms padding
        ),
    )

    # Start the session
    await session.start(
        room=ctx.room,
        agent=Assistant()
    )

    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the user warmly and ask how you can help."
    )

if __name__ == "__main__":
    # Run the agent
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))