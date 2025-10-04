#!/usr/bin/env python3
"""
Airbnb MCP Server - Python Implementation using Official MCP SDK
Enhanced version using Crawl4AI for superior scraping and caching.
"""

import sys
import logging
import io
import asyncio
import json
import shutil
import os
from typing import Optional, List, Any
from urllib.parse import urlencode
from contextlib import contextmanager

# Fix Windows UTF-8 encoding issues
if sys.platform == 'win32':
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Configure logging to stderr only (stdout is for MCP protocol)
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
from mcp import  Tool, types
from mcp.server.stdio import stdio_server

# Crawl4AI imports
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from pydantic import BaseModel, Field, HttpUrl

# Configuration
BASE_URL = "https://www.airbnb.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_TIMEOUT = 30.0
IGNORE_ROBOTS_TXT = "--ignore-robots-txt" in sys.argv

# Crawl4AI Setup - with verbose=False to suppress stdout output
browser_cfg = BrowserConfig(
    user_agent=USER_AGENT,
    headless=True,
    verbose=False,  # Suppress output to stdout
    accept_downloads=False,
    java_script_enabled=True  # Enable JavaScript execution (needed for React apps)
)
crawler = AsyncWebCrawler(config=browser_cfg)

# Robots.txt handling
robots_txt_content = ""
robots_error_message = "This path is disallowed by Airbnb's robots.txt. Run with '--ignore-robots-txt' to bypass."

@contextmanager
def suppress_stdout():
    """Context manager to redirect stdout to stderr temporarily"""
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout

async def fetch_robots_txt():
    """Fetch and parse robots.txt from Airbnb"""
    global robots_txt_content
    if IGNORE_ROBOTS_TXT:
        logger.info("Skipping robots.txt fetch (ignored by configuration)")
        return

    try:
        logger.info("Fetching robots.txt from Airbnb")
        
        # Use context manager to suppress Crawl4AI stdout
        with suppress_stdout():
            result = await crawler.arun(
                url=f"{BASE_URL}/robots.txt",
                config=CrawlerRunConfig(cache_mode=CacheMode.ENABLED, verbose=False)
            )
            
        if result.success:
            robots_txt_content = result.html if hasattr(result, 'html') else (result.markdown if hasattr(result, 'markdown') else "")
            logger.info("Successfully fetched robots.txt")
        else:
            raise Exception(result.error)
    except Exception as e:
        logger.warning(f"Error fetching robots.txt: {e}, assuming all paths allowed")
        robots_txt_content = ""

def is_path_allowed(path: str) -> bool:
    """Check if a path is allowed by robots.txt"""
    if IGNORE_ROBOTS_TXT or not robots_txt_content:
        return True
    for line in robots_txt_content.split('\n'):
        if line.lower().startswith('disallow:'):
            disallowed_path = line.split(':', 1)[1].strip()
            if path.startswith(disallowed_path):
                return False
    return True

async def get_next_data(url: str, cache_mode: CacheMode = CacheMode.ENABLED):
    """Shared function to scrape __NEXT_DATA__ from a URL using Crawl4AI"""
    # Note: We'll rely primarily on HTML fallback parsing since CSS extraction is unreliable
    schema = {
        "name": "GetNextData",
        "baseSelector": "html",
        "fields": [{
            "name": "script_content",
            "selector": "script#__NEXT_DATA__, script#initial-data, script[type='application/json']",
            "type": "text",
            "all": False  # Get first match
        }]
    }
    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(
        extraction_strategy=strategy, 
        cache_mode=cache_mode,
        verbose=False,  # Suppress progress output
        word_count_threshold=1,  # Don't filter by word count
        only_text=False,  # We need full HTML for fallback
        wait_until="networkidle",  # Wait for network to be idle (JS loaded)
        delay_before_return_html=2.0,  # Wait 2 seconds for JS to render
        page_timeout=60000  # 60 second timeout
    )
    
    # Use context manager to suppress Crawl4AI stdout
    with suppress_stdout():
        result = await crawler.arun(url, config)
    

    if not result.success:
        raise Exception(f"Failed to scrape data from {url}. Error: {result.error}")

    # Log extracted content for debugging
    logger.info(f"Extraction result for {url}: success={result.success}, has_content={bool(result.extracted_content)}")
    
    # Try to parse extraction result first
    extraction_failed = False
    try:
        if result.extracted_content:
            extracted_list = json.loads(result.extracted_content) if isinstance(result.extracted_content, str) else result.extracted_content
            
            # Check if we got valid data
            if extracted_list and isinstance(extracted_list, list) and len(extracted_list) > 0:
                if 'script_content' in extracted_list[0] and extracted_list[0]['script_content']:
                    script_text = extracted_list[0]['script_content']
                    json_data = json.loads(script_text)
                    return json_data.get('props', {}).get('pageProps', {})
            
            # If we got here, extraction returned something but it's empty or malformed
            logger.warning(f"Extracted data is empty or malformed: {result.extracted_content[:200]}")
            extraction_failed = True
        else:
            logger.warning("No extracted_content from strategy")
            extraction_failed = True
            
    except (json.JSONDecodeError, IndexError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse extraction result: {e}")
        extraction_failed = True
    
    # Fallback: Try to extract directly from HTML
    if extraction_failed:
        logger.info("Attempting HTML fallback parsing")
        import re
        html_content = result.html if hasattr(result, 'html') else ""
        
        if not html_content:
            raise Exception("No HTML content available for parsing")
        
        # Look for __NEXT_DATA__ or initial-data script tags with more flexible patterns
        patterns = [
            r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
            r'<script[^>]*id=["\']initial-data["\'][^>]*>(.*?)</script>',
            r'<script[^>]*type=["\']application/json["\'][^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if matches:
                try:
                    json_data = json.loads(matches[0])
                    logger.info("Successfully extracted data using HTML fallback")
                    return json_data.get('props', {}).get('pageProps', {})
                except json.JSONDecodeError as e:
                    logger.warning(f"Found script tag but failed to parse JSON: {e}")
                    continue
        
        # If all patterns failed, save HTML for debugging and log sample
        logger.error(f"Could not find valid script tags in {len(html_content)} chars of HTML")
        
        # Save HTML to file for debugging
        debug_file = "debug_airbnb_page.html"
        try:
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.error(f"Saved full HTML to {debug_file} for debugging")
        except Exception as e:
            logger.error(f"Could not save debug HTML: {e}")
        
        # Log sample
        logger.error(f"HTML sample (first 2000 chars):\n{html_content[:2000]}")
        raise Exception("Could not find __NEXT_DATA__ or initial-data script tag in HTML. Check debug_airbnb_page.html for full content.")

# Tool implementations
async def airbnb_search(location: str, checkin: Optional[str] = None, checkout: Optional[str] = None, 
                       guests: int = 1, limit: int = 10, ignoreRobotsText: bool = False, 
                       bypass_cache: bool = False) -> str:
    """Searches for Airbnb listings with various filters."""
    params = {
        "query": location,
        "adults": guests,
        "items_per_grid": limit,
    }
    if checkin: params["checkin"] = checkin
    if checkout: params["checkout"] = checkout

    search_url = f"{BASE_URL}/s/homes"
    full_url = f"{search_url}?{urlencode(params)}"

    if not (ignoreRobotsText or IGNORE_ROBOTS_TXT) and not is_path_allowed("/s/"):
        return json.dumps({'error': robots_error_message, 'url': full_url})

    try:
        cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.ENABLED
        page_props = await get_next_data(full_url, cache_mode)
        
        search_results = page_props.get("searchResults", {})
        listings = []
        if "sections" in search_results:
            for section in search_results["sections"]:
                if "items" in section:
                    for item in section["items"]:
                        try:
                            listing_data = item.get('listing', {})
                            if listing_data:
                                listings.append({
                                    "id": listing_data.get("id"),
                                    "name": listing_data.get("name"),
                                    "city": listing_data.get("city"),
                                    "price_formatted": listing_data.get("priceFormatted"),
                                    "url": f"{BASE_URL}/rooms/{listing_data.get('id')}",
                                    "image_url": listing_data.get("contextualPictures",[{}])[0].get("picture")
                                })
                        except Exception as e:
                            logger.warning(f"Skipping a listing due to parsing error: {e}")

        return json.dumps(listings[:limit], indent=2)
    except Exception as e:
        logger.error(f"Error during Airbnb search: {e}")
        return json.dumps({"error": str(e), "url": full_url}, indent=2)

async def airbnb_listing_details(id: str, ignoreRobotsText: bool = False, 
                                 bypass_cache: bool = False) -> str:
    """Fetches detailed information for a specific Airbnb listing."""
    listing_url = f"{BASE_URL}/rooms/{id}"
    
    if not (ignoreRobotsText or IGNORE_ROBOTS_TXT) and not is_path_allowed("/rooms/"):
        return json.dumps({'error': robots_error_message, 'url': listing_url})

    try:
        cache_mode = CacheMode.BYPASS if bypass_cache else CacheMode.ENABLED
        page_props = await get_next_data(listing_url, cache_mode)
        
        pdp_data = page_props.get("pdpRequest", {}).get("data", {}).get("presentation", {}).get("stayProductDetailPage", {})
        main_section = pdp_data.get("sections", {}).get("sections", [{}])[0]
        details = main_section.get("section", {})

        return json.dumps({
            "id": id,
            "name": details.get("name"),
            "description": details.get("description"),
            "room_type": details.get("roomType"),
            "person_capacity": details.get("personCapacity"),
            "reviews_count": details.get("reviewsCount"),
            "url": listing_url
        }, indent=2)
    except Exception as e:
        logger.error(f"Error fetching listing details for ID {id}: {e}")
        return json.dumps({"error": str(e), "url": listing_url}, indent=2)

async def _fetch_listing_detail_dict(listing_id: str) -> dict:
    """Internal function to fetch listing details as dict"""
    listing_url = f"{BASE_URL}/rooms/{listing_id}"
    
    if not IGNORE_ROBOTS_TXT and not is_path_allowed("/rooms/"):
        return {'error': robots_error_message, 'url': listing_url}

    try:
        page_props = await get_next_data(listing_url, CacheMode.ENABLED)
        pdp_data = page_props.get("pdpRequest", {}).get("data", {}).get("presentation", {}).get("stayProductDetailPage", {})
        main_section = pdp_data.get("sections", {}).get("sections", [{}])[0]
        details = main_section.get("section", {})

        return {
            "id": listing_id,
            "name": details.get("name"),
            "description": details.get("description"),
            "room_type": details.get("roomType"),
            "person_capacity": details.get("personCapacity"),
            "reviews_count": details.get("reviewsCount"),
            "url": listing_url
        }
    except Exception as e:
        logger.error(f"Error fetching listing details for ID {listing_id}: {e}")
        return {"error": str(e), "url": listing_url}

async def airbnb_compare_listings(ids: List[str]) -> str:
    """Compares up to 5 Airbnb listings side-by-side."""
    if len(ids) > 5:
        return json.dumps({"error": "You can compare a maximum of 5 listings at a time."})

    try:
        logger.info(f"Starting parallel fetch for {len(ids)} listings.")
        results = await asyncio.gather(*[_fetch_listing_detail_dict(id) for id in ids])
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Error during listing comparison: {e}")
        return json.dumps({"error": str(e)})

def clear_cache_sync() -> str:
    """Clears the Crawl4AI cache directory."""
    cache_dir = ".crawl4ai_cache"
    try:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            logger.info(f"Successfully cleared cache directory: {cache_dir}")
            return "Cache cleared successfully."
        else:
            logger.info("Cache directory does not exist, nothing to clear.")
            return "Cache directory not found."
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return f"Error clearing cache: {e}"

# Create MCP server
app = Server("airbnb_mcp_server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="airbnb_search",
            description="Search for Airbnb listings with various filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "Location to search (e.g., 'San Francisco, CA')"},
                    "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                    "guests": {"type": "number", "description": "Number of guests (default: 1)"},
                    "limit": {"type": "number", "description": "Number of results (default: 10)"},
                    "ignoreRobotsText": {"type": "boolean", "description": "Ignore robots.txt"},
                    "bypass_cache": {"type": "boolean", "description": "Bypass cache"}
                },
                "required": ["location"]
            }
        ),
        types.Tool(
            name="airbnb_listing_details",
            description="Get detailed information about a specific Airbnb listing",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Airbnb listing ID"},
                    "ignoreRobotsText": {"type": "boolean", "description": "Ignore robots.txt"},
                    "bypass_cache": {"type": "boolean", "description": "Bypass cache"}
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="airbnb_compare_listings",
            description="Compare up to 5 Airbnb listings side-by-side",
            inputSchema={
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of listing IDs to compare (max 5)"
                    }
                },
                "required": ["ids"]
            }
        ),
        types.Tool(
            name="clear_cache",
            description="Clear the Crawl4AI cache directory",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "airbnb_search":
            result = await airbnb_search(**arguments)
        elif name == "airbnb_listing_details":
            result = await airbnb_listing_details(**arguments)
        elif name == "airbnb_compare_listings":
            result = await airbnb_compare_listings(**arguments)
        elif name == "clear_cache":
            result = clear_cache_sync()
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [types.TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point"""
    logger.info("Starting Airbnb MCP Server with Official SDK")
    logger.info(f"Robots.txt compliance: {'DISABLED' if IGNORE_ROBOTS_TXT else 'ENABLED'}")
    
    # Initialize crawler and fetch robots.txt
    await fetch_robots_txt()
    
    # Run the MCP server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
