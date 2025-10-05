"""
Airbnb listing details tool
"""

import json
import logging
from typing import Optional
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from config import BASE_URL
from utils import fetch_with_user_agent, clean_object, pick_by_schema, flatten_arrays_in_object, get_listing_details_schema

logger = logging.getLogger(__name__)


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

        # Get schema
        allow_section_schema = get_listing_details_schema()

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
