"""
Airbnb search tool
"""

import json
import base64
import logging
from typing import Optional
from urllib.parse import quote, urlencode
from bs4 import BeautifulSoup

from config import BASE_URL
from utils import fetch_with_user_agent, clean_object, pick_by_schema, flatten_arrays_in_object, get_search_result_schema

logger = logging.getLogger(__name__)


async def airbnb_search(location: str, checkin: Optional[str] = None, checkout: Optional[str] = None,
                       adults: int = 1, children: int = 0, limit: int = 10) -> str:
    """Search for Airbnb listings using simple HTTP fetch"""

    # Build search URL
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
        results = client_data['data']['presentation']['staysSearch']['results']

        # Clean results
        clean_object(results)

        # Extract and process search results
        search_results = results.get('searchResults', [])
        logger.info(f"Found {len(search_results)} raw search results")

        # Get schema
        allow_search_result_schema = get_search_result_schema()

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

                # Decode listing ID (base64 encoded)
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
