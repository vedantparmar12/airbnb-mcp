#!/usr/bin/env python3
"""
Airbnb MCP Server - Simple HTTP Fetch Version (like TypeScript implementation)
Based on the working TypeScript version that uses simple HTTP fetch + HTML parsing
"""

import sys
import logging
import io
import asyncio
import json
from typing import Optional, List
from urllib.parse import urlencode, quote
import base64

# Fix Windows UTF-8 encoding issues
if sys.platform == 'win32':
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
    encoding='utf-8',
    errors='replace'
)
logger = logging.getLogger(__name__)

# MCP SDK imports
from mcp.server import Server
from mcp import types
from mcp.server.stdio import stdio_server

# HTTP and HTML parsing
import aiohttp
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://www.airbnb.com"
USER_AGENT = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
REQUEST_TIMEOUT = 30
IGNORE_ROBOTS_TXT = "--ignore-robots-txt" in sys.argv

# Create MCP server
app = Server("airbnb_mcp_server")

async def fetch_with_user_agent(url: str, timeout: int = 30) -> str:
    """Fetch URL with proper headers"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cache-Control": "no-cache",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.reason}")
            return await response.text()

# Utility functions (ported from util.ts)
def clean_object(obj):
    """Remove null/undefined values and __typename fields"""
    if isinstance(obj, dict):
        keys_to_delete = []
        for key, value in obj.items():
            if value is None or key == "__typename":
                keys_to_delete.append(key)
            elif isinstance(value, (dict, list)):
                clean_object(value)
        for key in keys_to_delete:
            del obj[key]
    elif isinstance(obj, list):
        for item in obj:
            clean_object(item)
    return obj

def pick_by_schema(obj, schema):
    """Filter object to only include fields specified in schema"""
    if not isinstance(obj, dict) or obj is None:
        return obj

    if isinstance(obj, list):
        return [pick_by_schema(item, schema) for item in obj]

    result = {}
    for key, rule in schema.items():
        if key in obj:
            if rule is True:
                result[key] = obj[key]
            elif isinstance(rule, dict):
                result[key] = pick_by_schema(obj[key], rule)
    return result

def flatten_arrays_in_object(input_obj, in_array=False):
    """Flatten nested arrays and objects into readable strings"""
    if isinstance(input_obj, list):
        flat_items = [flatten_arrays_in_object(item, True) for item in input_obj]
        return ', '.join(str(item) for item in flat_items)
    elif isinstance(input_obj, dict):
        if in_array:
            values = [flatten_arrays_in_object(v, True) for v in input_obj.values()]
            return ': '.join(str(v) for v in values)
        else:
            result = {}
            for key, value in input_obj.items():
                result[key] = flatten_arrays_in_object(value, False)
            return result
    else:
        return input_obj

async def airbnb_search(location: str, checkin: Optional[str] = None, checkout: Optional[str] = None,
                       adults: int = 1, children: int = 0, limit: int = 10) -> str:
    """Search for Airbnb listings using simple HTTP fetch"""

    # Build search URL (like TypeScript version)
    search_url = f"{BASE_URL}/s/{quote(location)}/homes?"

    params = {}
    if checkin:
        params["checkin"] = checkin
    if checkout:
        params["checkout"] = checkout
    if adults:
        params["adults"] = str(adults)
    if children:
        params["children"] = str(children)

    full_url = search_url + urlencode(params)

    # Schema for filtering results (updated for current Airbnb structure)
    allow_search_result_schema = {
        "demandStayListing": {
            "id": True,
            "location": True,
            "description": True,
            "nameLocale": True,
        },
        "propertyId": True,
        "title": True,
        "nameLocalized": True,
        "structuredContent": {
            "primaryLine": {
                "body": True
            },
            "secondaryLine": {
                "body": True
            },
        },
        "avgRatingA11yLabel": True,
        "avgRatingLocalized": True,
        "badges": {
            "text": True,
        },
        "contextualPictures": {
            "picture": True
        },
        "structuredDisplayPrice": {
            "primaryLine": {
                "accessibilityLabel": True,
                "discountedPrice": True,
                "originalPrice": True,
                "qualifier": True,
            },
            "secondaryLine": {
                "accessibilityLabel": True,
            },
        },
    }

    try:
        logger.info(f"Fetching {full_url}")

        # Fetch HTML (fast!)
        html = await fetch_with_user_agent(full_url)

        logger.info(f"Got HTML response, length: {len(html)} chars")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find the data script element (like TypeScript: $("#data-deferred-state-0"))
        script_elem = soup.find('script', {'id': 'data-deferred-state-0'})

        if not script_elem:
            logger.error("Could not find #data-deferred-state-0 script element")
            raise Exception("Could not find data script element - page structure may have changed")

        logger.info("Found data script element")

        # Parse JSON from script content
        script_content = script_elem.string
        if not script_content:
            raise Exception("Data script element is empty")

        logger.info(f"Script content length: {len(script_content)} chars")

        # Parse like TypeScript: JSON.parse(scriptContent).niobeClientData[0][1]
        data = json.loads(script_content)

        if 'niobeClientData' not in data:
            logger.error(f"No niobeClientData in parsed JSON. Keys: {list(data.keys())}")
            raise Exception("Unexpected data structure - niobeClientData not found")

        client_data = data['niobeClientData'][0][1]
        results = client_data['data']['presentation']['staysSearch']['results']

        # Clean results
        clean_object(results)

        # Extract and process search results (like TypeScript version)
        search_results = results.get('searchResults', [])

        logger.info(f"Found {len(search_results)} raw search results")

        listings = []
        for idx, result in enumerate(search_results[:limit]):
            try:
                # Extract listing data from demandStayListing field
                demand_stay_listing = result.get('demandStayListing', {})
                if not demand_stay_listing:
                    logger.warning(f"Result {idx}: No 'demandStayListing' field found")
                    continue

                listing_id_encoded = demand_stay_listing.get('id', '')
                if not listing_id_encoded:
                    logger.warning(f"Result {idx}: No 'id' in demandStayListing")
                    continue

                # Decode listing ID (base64 encoded) - like TypeScript: atob(result.listing.id).split(":")[1]
                try:
                    decoded = base64.b64decode(listing_id_encoded).decode('utf-8')
                    listing_id = decoded.split(':')[1] if ':' in decoded else listing_id_encoded
                except Exception as e:
                    logger.warning(f"Failed to decode listing ID: {e}")
                    listing_id = listing_id_encoded

                # Apply schema filtering
                filtered_result = pick_by_schema(result, allow_search_result_schema)
                flattened_result = flatten_arrays_in_object(filtered_result)

                # Build listing object with all extracted data
                listing = {
                    'id': listing_id,
                    'url': f"{BASE_URL}/rooms/{listing_id}",
                    **flattened_result
                }

                listings.append(listing)
                logger.info(f"Successfully extracted listing {idx}: {listing_id}")

            except Exception as e:
                logger.warning(f"Error parsing listing {idx}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue

        logger.info(f"Successfully extracted {len(listings)} listings from {len(search_results)} raw results")

        # Include pagination info if available
        pagination_info = results.get('paginationInfo', {})

        return json.dumps({
            'searchUrl': full_url,
            'searchResults': listings,
            'paginationInfo': pagination_info
        }, indent=2)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return json.dumps({
            'error': str(e),
            'searchUrl': full_url
        }, indent=2)

async def airbnb_listing_details(id: str, checkin: Optional[str] = None, checkout: Optional[str] = None,
                                 adults: int = 1, children: int = 0) -> str:
    """Get detailed information about a specific Airbnb listing"""

    # Build listing URL
    listing_url = f"{BASE_URL}/rooms/{id}?"

    params = {}
    if checkin:
        params["check_in"] = checkin
    if checkout:
        params["check_out"] = checkout
    if adults:
        params["adults"] = str(adults)
    if children:
        params["children"] = str(children)

    full_url = listing_url + urlencode(params)

    # Schema for filtering listing details sections
    allow_section_schema = {
        "LOCATION_DEFAULT": {
            "lat": True,
            "lng": True,
            "subtitle": True,
            "title": True
        },
        "POLICIES_DEFAULT": {
            "title": True,
            "houseRulesSections": {
                "title": True,
                "items": {
                    "title": True
                }
            }
        },
        "HIGHLIGHTS_DEFAULT": {
            "highlights": {
                "title": True
            }
        },
        "DESCRIPTION_DEFAULT": {
            "htmlDescription": {
                "htmlText": True
            }
        },
        "AMENITIES_DEFAULT": {
            "title": True,
            "seeAllAmenitiesGroups": {
                "title": True,
                "amenities": {
                    "title": True
                }
            }
        },
    }

    try:
        logger.info(f"Fetching listing details for ID: {id}")

        # Fetch HTML
        html = await fetch_with_user_agent(full_url)

        logger.info(f"Got HTML response, length: {len(html)} chars")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find the data script element
        script_elem = soup.find('script', {'id': 'data-deferred-state-0'})

        if not script_elem:
            logger.error("Could not find #data-deferred-state-0 script element")
            raise Exception("Could not find data script element - page structure may have changed")

        logger.info("Found data script element")

        # Parse JSON from script content
        script_content = script_elem.string
        if not script_content:
            raise Exception("Data script element is empty")

        logger.info(f"Script content length: {len(script_content)} chars")

        # Parse JSON
        data = json.loads(script_content)

        if 'niobeClientData' not in data:
            logger.error(f"No niobeClientData in parsed JSON. Keys: {list(data.keys())}")
            raise Exception("Unexpected data structure - niobeClientData not found")

        client_data = data['niobeClientData'][0][1]

        # Navigate to listing details sections
        try:
            sections_data = client_data['data']['presentation']['stayProductDetailPage']['sections']['sections']
        except KeyError as e:
            logger.error(f"Could not find sections in data structure: {e}")
            raise Exception(f"Listing details not found - may be unavailable or structure changed")

        # Clean sections
        for section in sections_data:
            clean_object(section)

        # Filter and process sections based on schema
        details = []
        for section in sections_data:
            section_id = section.get('sectionId', '')
            if section_id in allow_section_schema:
                section_content = section.get('section', {})
                filtered_section = pick_by_schema(section_content, allow_section_schema[section_id])
                flattened_section = flatten_arrays_in_object(filtered_section)

                details.append({
                    'id': section_id,
                    **flattened_section
                })

        logger.info(f"Successfully extracted {len(details)} detail sections")

        return json.dumps({
            'listingUrl': full_url,
            'listingId': id,
            'details': details
        }, indent=2)

    except Exception as e:
        logger.error(f"Listing details fetch failed: {e}")
        return json.dumps({
            'error': str(e),
            'listingUrl': full_url,
            'listingId': id
        }, indent=2)

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
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "airbnb_search":
            result = await airbnb_search(**arguments)
        elif name == "airbnb_listing_details":
            result = await airbnb_listing_details(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point"""
    logger.info("Starting Airbnb MCP Server (Simple HTTP Fetch Version)")
    logger.info("Based on the working TypeScript implementation")
    
    # Run the MCP server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
