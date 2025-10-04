#!/usr/bin/env python3
"""
Airbnb MCP Server - Python FastMCP Implementation
Enhanced version using Crawl4AI for superior scraping and caching.
"""

import sys
import logging
import io

# Fix Windows UTF-8 encoding issues
if sys.platform == 'win32':
    # Ensure stdout and stderr use UTF-8 encoding
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- Definitive Logging Configuration ---
# This is the master fix for all previous errors.
# 1. Directs all log output to stderr, keeping stdout clean for MCP JSON communication.
# 2. Sets encoding to utf-8 to prevent UnicodeEncodeError on Windows.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
    encoding='utf-8',
    errors='replace'
)

import asyncio
import json
import shutil
import os
from typing import Optional, List, Any, Dict
from urllib.parse import urlencode, urlparse
from pydantic import BaseModel, Field, HttpUrl

# Disable FastMCP's fancy output to prevent unicode errors on Windows
os.environ['FASTMCP_NO_COLOR'] = '1'
os.environ['FASTMCP_QUIET'] = '1'

from fastmcp import FastMCP
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# --- Configuration ---
logger = logging.getLogger(__name__)

BASE_URL = "https://www.airbnb.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 30.0
IGNORE_ROBOTS_TXT = "--ignore-robots-txt" in sys.argv

# --- Crawl4AI Setup ---
browser_cfg = BrowserConfig(
    user_agent=USER_AGENT,
    headless=True
)
crawler = AsyncWebCrawler(config=browser_cfg)

# --- Robots.txt Handling ---
robots_txt_content = ""
robots_error_message = "This path is disallowed by Airbnb's robots.txt. Run with '--ignore-robots-txt' to bypass."

async def fetch_robots_txt():
    """Fetch and parse robots.txt from Airbnb using Crawl4AI"""
    global robots_txt_content
    if IGNORE_ROBOTS_TXT:
        logger.info("Skipping robots.txt fetch (ignored by configuration)")
        return

    try:
        logger.info("Fetching robots.txt from Airbnb")
        result = await crawler.arun(
            url=f"{BASE_URL}/robots.txt",
            config=CrawlerRunConfig(
                cache_mode=CacheMode.ENABLED
            )
        )
        if result.success:
            robots_txt_content = result.text
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
    # Simplified check
    for line in robots_txt_content.split('\n'):
        if line.lower().startswith('disallow:'):
            disallowed_path = line.split(':', 1)[1].strip()
            if path.startswith(disallowed_path):
                return False
    return True

# --- Pydantic Models for Data Extraction ---
class ListingPhoto(BaseModel):
    picture_url: Optional[HttpUrl] = Field(None, alias='picture')

class Listing(BaseModel):
    id: str
    name: str = Field(..., alias='name')
    city: str = Field(..., alias='city')
    photos: List[ListingPhoto] = Field([], alias='contextualPictures')
    price: int = Field(..., alias='price')
    price_formatted: str = Field(..., alias='priceFormatted')

class ReviewScores(BaseModel):
    score_accuracy: Optional[int] = Field(None, alias='accuracy')
    score_cleanliness: Optional[int] = Field(None, alias='cleanliness')
    score_checkin: Optional[int] = Field(None, alias='checkin')
    score_communication: Optional[int] = Field(None, alias='communication')
    score_location: Optional[int] = Field(None, alias='location')
    score_value: Optional[int] = Field(None, alias='value')
    score_rating: Optional[int] = Field(None, alias='rating')

class ListingDetails(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    room_type: Optional[str] = Field(None, alias='roomType')
    person_capacity: int = Field(1, alias='personCapacity')
    photos: List[ListingPhoto] = Field([], alias='photos')
    reviews_count: int = Field(0, alias='reviewsCount')
    reviews: ReviewScores = Field({}, alias='reviewDetails')

# --- MCP Server and Tools ---
mcp = FastMCP(
    name="airbnb_mcp_server"
)

async def get_next_data(url: str, cache_mode: CacheMode = CacheMode.ENABLED):
    """Shared function to scrape __NEXT_DATA__ from a URL using Crawl4AI."""
    schema = {
        "name": "GetNextData",
        "baseSelector": "body",
        "fields": [
            {
                "name": "script_content",
                "selector": "script#initial-data, script#__NEXT_DATA__",
                "type": "text"
            }
        ]
    }
    strategy = JsonCssExtractionStrategy(schema=schema)
    
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode=cache_mode
    )
    result = await crawler.arun(url, config)

    if not result.success or not result.extracted_content:
        raise Exception(f"Failed to scrape data from {url}. Error: {result.error}")

    # The strategy returns a JSON string like '[{"script_content": "..."}]'.
    # We need to parse it, get the content, and parse that content as JSON.
    try:
        extracted_list = json.loads(result.extracted_content)
        if not extracted_list or 'script_content' not in extracted_list[0]:
            raise Exception("Could not find script_content in extracted data.")
        
        script_text = extracted_list[0]['script_content']
        json_data = json.loads(script_text)

        # The actual data is nested deep inside
        return json_data.get('props', {}).get('pageProps', {})
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        raise Exception(f"Failed to parse __NEXT_DATA__ from page. Error: {e}")

@mcp.tool
async def airbnb_search(location: str, checkin: Optional[str] = None, checkout: Optional[str] = None, guests: int = 1, limit: int = 10, ignoreRobotsText: bool = False, bypass_cache: bool = False):
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

@mcp.tool
async def airbnb_listing_details(id: str, ignoreRobotsText: bool = False, bypass_cache: bool = False):
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

async def _fetch_listing_detail(listing_id: str):
    """Internal function to fetch listing details without MCP wrapper"""
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

@mcp.tool
async def airbnb_compare_listings(ids: List[str]):
    """Compares up to 5 Airbnb listings side-by-side."""
    if len(ids) > 5:
        return json.dumps({"error": "You can compare a maximum of 5 listings at a time."})

    try:
        logger.info(f"Starting parallel fetch for {len(ids)} listings.")
        # Use the internal function to avoid recursive MCP tool calls
        results = await asyncio.gather(*[_fetch_listing_detail(id) for id in ids])
        
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Error during listing comparison: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool
def clear_cache():
    """Clears the Crawl4AI cache directory."""
    cache_dir = ".crawl4ai_cache"
    try:
        if shutil.os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            logger.info(f"Successfully cleared cache directory: {cache_dir}")
            return "Cache cleared successfully."
        else:
            logger.info("Cache directory does not exist, nothing to clear.")
            return "Cache directory not found."
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return f"Error clearing cache: {e}"

if __name__ == "__main__":
    logger.info("Starting Airbnb Enhanced MCP Server with Crawl4AI")
    logger.info(f"Robots.txt compliance: {'DISABLED' if IGNORE_ROBOTS_TXT else 'ENABLED'}")

    async def startup():
        await fetch_robots_txt()

    asyncio.run(startup())
    
    # Run with stdio transport (standard MCP protocol)
    mcp.run(transport='stdio')