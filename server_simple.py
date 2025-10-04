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
            # Try alternative selectors
            script_elem = soup.find('script', {'id': 'data-state'})
            if not script_elem:
                logger.error("Could not find any data script elements")
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
        
        # Extract search results
        search_results = results.get('searchResults', [])
        
        listings = []
        for result in search_results[:limit]:
            try:
                # Extract listing data
                listing_data = result.get('listing', {})
                if not listing_data:
                    continue
                
                # Decode listing ID (base64 encoded)
                listing_id_encoded = listing_data.get('id', '')
                if listing_id_encoded:
                    try:
                        decoded = base64.b64decode(listing_id_encoded).decode('utf-8')
                        listing_id = decoded.split(':')[1] if ':' in decoded else listing_id_encoded
                    except:
                        listing_id = listing_id_encoded
                else:
                    listing_id = None
                
                # Build listing object
                listing = {
                    'id': listing_id,
                    'name': listing_data.get('name', ''),
                    'city': listing_data.get('city', ''),
                    'url': f"{BASE_URL}/rooms/{listing_id}" if listing_id else None,
                }
                
                # Try to get price
                if 'structuredDisplayPrice' in result:
                    price_info = result['structuredDisplayPrice'].get('primaryLine', {})
                    listing['price_formatted'] = price_info.get('accessibilityLabel', '')
                
                # Try to get image
                if 'contextualPictures' in result and result['contextualPictures']:
                    listing['image_url'] = result['contextualPictures'][0].get('picture', '')
                
                if listing['id']:
                    listings.append(listing)
                    
            except Exception as e:
                logger.warning(f"Error parsing listing: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(listings)} listings")
        
        return json.dumps({
            'searchUrl': full_url,
            'results': listings,
            'count': len(listings)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return json.dumps({
            'error': str(e),
            'searchUrl': full_url
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
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "airbnb_search":
            result = await airbnb_search(**arguments)
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
