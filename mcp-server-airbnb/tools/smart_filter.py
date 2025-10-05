"""
Airbnb smart filter tool
"""

import json
import logging
import re
from typing import Optional

from .search import airbnb_search

logger = logging.getLogger(__name__)


async def airbnb_smart_filter(location: str, checkin: Optional[str] = None, checkout: Optional[str] = None,
                              adults: int = 1, children: int = 0,
                              min_price: Optional[float] = None, max_price: Optional[float] = None,
                              min_rating: Optional[float] = None,
                              sort_by: str = "value") -> str:
    """
    Smart filtered search with sorting
    sort_by options: 'price' (low to high), 'rating' (high to low), 'value' (rating/price ratio)
    """

    try:
        logger.info(f"Smart filter search for {location} with filters")

        # Perform base search
        result_json = await airbnb_search(location, checkin, checkout, adults, children, limit=50)
        result = json.loads(result_json)

        if 'error' in result:
            return result_json

        listings = result.get('searchResults', [])

        if not listings:
            return json.dumps({
                'error': 'No listings found for this location',
                'location': location
            }, indent=2)

        # Filter and score listings
        filtered_listings = []

        for listing in listings:
            # Extract price
            price_info = listing.get('structuredDisplayPrice', {}).get('primaryLine', {})
            price_str = price_info.get('discountedPrice', '')

            if not price_str:
                continue

            price_match = re.search(r'[\d,]+', price_str.replace(',', ''))
            if not price_match:
                continue

            total_price = float(price_match.group().replace(',', ''))

            # Extract rating
            rating_str = listing.get('avgRatingLocalized', '')
            rating = 0.0
            if rating_str:
                rating_match = re.search(r'([\d.]+)', rating_str)
                if rating_match:
                    rating = float(rating_match.group(1))

            # Apply filters
            if min_price and total_price < min_price:
                continue
            if max_price and total_price > max_price:
                continue
            if min_rating and rating < min_rating:
                continue

            # Calculate value score (higher is better)
            value_score = (rating / (total_price / 1000)) if total_price > 0 else 0

            filtered_listings.append({
                **listing,
                '_price_numeric': total_price,
                '_rating_numeric': rating,
                '_value_score': value_score
            })

        # Sort listings
        if sort_by == "price":
            filtered_listings.sort(key=lambda x: x['_price_numeric'])
        elif sort_by == "rating":
            filtered_listings.sort(key=lambda x: x['_rating_numeric'], reverse=True)
        elif sort_by == "value":
            filtered_listings.sort(key=lambda x: x['_value_score'], reverse=True)

        # Remove internal fields before returning
        for listing in filtered_listings:
            listing.pop('_price_numeric', None)
            listing.pop('_rating_numeric', None)
            listing.pop('_value_score', None)

        logger.info(f"Found {len(filtered_listings)} listings matching filters")

        return json.dumps({
            'searchUrl': result.get('searchUrl'),
            'filters_applied': {
                'min_price': min_price,
                'max_price': max_price,
                'min_rating': min_rating,
                'sort_by': sort_by
            },
            'total_found': len(filtered_listings),
            'searchResults': filtered_listings[:20],  # Limit to top 20
            'paginationInfo': result.get('paginationInfo', {})
        }, indent=2)

    except Exception as e:
        logger.error(f"Smart filter search failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({
            'error': str(e),
            'location': location
        }, indent=2)
