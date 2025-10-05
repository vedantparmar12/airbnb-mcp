"""
Airbnb compare listings tool
"""

import json
import logging
import re
from typing import List, Optional

from .search import airbnb_search
from .listing_details import airbnb_listing_details

logger = logging.getLogger(__name__)


async def airbnb_compare_listings(listing_ids: List[str], checkin: Optional[str] = None,
                                  checkout: Optional[str] = None,
                                  adults: int = 1, children: int = 0) -> str:
    """Compare multiple listings side-by-side"""

    if not listing_ids or len(listing_ids) < 2:
        return json.dumps({
            'error': 'Please provide at least 2 listing IDs to compare',
            'format': 'listing_ids: ["id1", "id2", "id3"]'
        }, indent=2)

    if len(listing_ids) > 5:
        return json.dumps({
            'error': 'Maximum 5 listings can be compared at once',
            'provided': len(listing_ids)
        }, indent=2)

    try:
        logger.info(f"Comparing {len(listing_ids)} listings")

        comparisons = []

        for listing_id in listing_ids:
            # Get details for each listing
            details_json = await airbnb_listing_details(listing_id, checkin, checkout, adults, children)
            details = json.loads(details_json)

            if 'error' in details:
                logger.warning(f"Could not fetch details for {listing_id}: {details['error']}")
                continue

            # Also search to get pricing
            search_json = await airbnb_search("India", checkin, checkout, adults, children, limit=50)
            search = json.loads(search_json)

            listing_info = None
            for item in search.get('searchResults', []):
                if item.get('id') == listing_id:
                    listing_info = item
                    break

            # Extract key comparison data
            comparison = {
                'listing_id': listing_id,
                'url': details.get('listingUrl'),
                'name': 'Unknown',
                'price': None,
                'rating': None,
                'location': None,
                'amenities': [],
                'highlights': [],
                'policies': {}
            }

            if listing_info:
                comparison['name'] = listing_info.get('title', 'Unknown')
                comparison['rating'] = listing_info.get('avgRatingLocalized')

                # Extract price
                price_info = listing_info.get('structuredDisplayPrice', {}).get('primaryLine', {})
                comparison['price'] = price_info.get('discountedPrice')

            # Extract from details
            for detail in details.get('details', []):
                detail_id = detail.get('id')

                if detail_id == 'LOCATION_DEFAULT':
                    comparison['location'] = {
                        'lat': detail.get('lat'),
                        'lng': detail.get('lng'),
                        'description': detail.get('title')
                    }
                elif detail_id == 'AMENITIES_DEFAULT':
                    amenities_groups = detail.get('seeAllAmenitiesGroups', [])
                    if isinstance(amenities_groups, str):
                        comparison['amenities'] = [amenities_groups]
                    else:
                        comparison['amenities'] = amenities_groups
                elif detail_id == 'HIGHLIGHTS_DEFAULT':
                    comparison['highlights'] = detail.get('highlights', [])
                elif detail_id == 'POLICIES_DEFAULT':
                    comparison['policies'] = detail.get('houseRulesSections', {})

            comparisons.append(comparison)

        if len(comparisons) < 2:
            return json.dumps({
                'error': 'Could not fetch enough listings to compare',
                'fetched': len(comparisons),
                'requested': len(listing_ids)
            }, indent=2)

        # Calculate comparison insights
        prices = []
        for comp in comparisons:
            if comp['price']:
                price_match = re.search(r'[\d,]+', comp['price'].replace(',', ''))
                if price_match:
                    prices.append({
                        'id': comp['listing_id'],
                        'value': float(price_match.group().replace(',', ''))
                    })

        insights = {}
        if prices:
            cheapest = min(prices, key=lambda x: x['value'])
            most_expensive = max(prices, key=lambda x: x['value'])
            insights = {
                'cheapest_listing_id': cheapest['id'],
                'most_expensive_listing_id': most_expensive['id'],
                'price_difference': round(most_expensive['value'] - cheapest['value'], 2)
            }

        logger.info(f"Successfully compared {len(comparisons)} listings")

        return json.dumps({
            'comparison_date': checkin if checkin else 'Not specified',
            'guests': {'adults': adults, 'children': children},
            'listings_compared': len(comparisons),
            'comparisons': comparisons,
            'insights': insights
        }, indent=2)

    except Exception as e:
        logger.error(f"Listing comparison failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({
            'error': str(e)
        }, indent=2)
