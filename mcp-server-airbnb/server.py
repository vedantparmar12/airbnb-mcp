# Fast startup: Fix Windows encoding FIRST, then import modules
import sys
import io

# Fix Windows UTF-8 encoding issues BEFORE any logging
if sys.platform == 'win32':
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Now import everything else
from config import LOG_LEVEL, LOG_FORMAT
import logging
import asyncio
import json
from mcp.server import Server
from mcp import types
from mcp.server.stdio import stdio_server

# Defer tool imports until needed (lazy loading)
# This speeds up initial server startup
_tools_loaded = False
_tool_functions = {}

def _load_tools():
    """Lazy load tools only when needed"""
    global _tools_loaded, _tool_functions
    if not _tools_loaded:
        from tools import (
            airbnb_search,
            airbnb_listing_details,
            airbnb_price_analyzer,
            airbnb_trip_budget,
            airbnb_smart_filter,
            airbnb_compare_listings
        )
        _tool_functions = {
            "airbnb_search": airbnb_search,
            "airbnb_listing_details": airbnb_listing_details,
            "airbnb_price_analyzer": airbnb_price_analyzer,
            "airbnb_trip_budget": airbnb_trip_budget,
            "airbnb_smart_filter": airbnb_smart_filter,
            "airbnb_compare_listings": airbnb_compare_listings,
        }
        _tools_loaded = True
    return _tool_functions

# Minimal logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.WARNING),  # Less verbose by default
    format=LOG_FORMAT,
    stream=sys.stderr,
    encoding='utf-8',
    errors='replace'
)
logger = logging.getLogger(__name__)



# Import all tools


# Create MCP server
app = Server("airbnb_mcp_server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="airbnb_search",
            description="Search for Airbnb listings (simple HTTP fetch - fast!)",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location to search (e.g., 'Goa, India')"},
                    "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "adults": {"type": "number", "description": "Number of adults (default: 1)"},
                    "children": {"type": "number", "description": "Number of children (default: 0)"},
                    "limit": {"type": "number", "description": "Number of results (default: 10)"}
                },
                "required": ["location"]
            }
        ),
        types.Tool(
            name="airbnb_listing_details",
            description="Get detailed information about a specific Airbnb listing including amenities, policies, location, and description",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "The Airbnb listing ID"},
                    "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "adults": {"type": "number", "description": "Number of adults (default: 1)"},
                    "children": {"type": "number", "description": "Number of children (default: 0)"}
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="airbnb_price_analyzer",
            description="Analyze and compare prices across different dates to find the cheapest and best value dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location to search (e.g., 'Goa, India')"},
                    "adults": {"type": "number", "description": "Number of adults (default: 1)"},
                    "children": {"type": "number", "description": "Number of children (default: 0)"},
                    "date_ranges": {
                        "type": "array",
                        "description": "List of date ranges to compare",
                        "items": {
                            "type": "object",
                            "properties": {
                                "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                                "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"}
                            },
                            "required": ["checkin", "checkout"]
                        }
                    }
                },
                "required": ["location", "date_ranges"]
            }
        ),
        types.Tool(
            name="airbnb_trip_budget",
            description="Calculate comprehensive trip budget including accommodation, service fees, taxes, and per-person breakdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "listing_id": {"type": "string", "description": "The Airbnb listing ID"},
                    "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "adults": {"type": "number", "description": "Number of adults (default: 1)"},
                    "children": {"type": "number", "description": "Number of children (default: 0)"},
                    "currency": {"type": "string", "description": "Currency code (default: INR)"}
                },
                "required": ["listing_id", "checkin", "checkout"]
            }
        ),
        types.Tool(
            name="airbnb_smart_filter",
            description="Advanced search with price/rating filters and smart sorting (by price, rating, or value)",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location to search (e.g., 'Goa, India')"},
                    "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "adults": {"type": "number", "description": "Number of adults (default: 1)"},
                    "children": {"type": "number", "description": "Number of children (default: 0)"},
                    "min_price": {"type": "number", "description": "Minimum price filter"},
                    "max_price": {"type": "number", "description": "Maximum price filter"},
                    "min_rating": {"type": "number", "description": "Minimum rating filter (e.g., 4.5)"},
                    "sort_by": {"type": "string", "description": "Sort by: 'price', 'rating', or 'value' (default: value)"}
                },
                "required": ["location"]
            }
        ),
        types.Tool(
            name="airbnb_compare_listings",
            description="Compare 2-5 listings side-by-side with prices, ratings, amenities, and policies",
            inputSchema={
                "type": "object",
                "properties": {
                    "listing_ids": {
                        "type": "array",
                        "description": "List of listing IDs to compare (2-5 listings)",
                        "items": {"type": "string"}
                    },
                    "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "adults": {"type": "number", "description": "Number of adults (default: 1)"},
                    "children": {"type": "number", "description": "Number of children (default: 0)"}
                },
                "required": ["listing_ids"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        # Load tools on first call (lazy loading)
        tools = _load_tools()
        
        if name not in tools:
            raise ValueError(f"Unknown tool: {name}")
        
        # Execute the tool
        result = await tools[name](**arguments)
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Main entry point - Fast startup with minimal logging"""
    # Minimal logging - server is ready immediately
    logger.debug("Airbnb MCP Server starting...")
    
    # Run the MCP server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
