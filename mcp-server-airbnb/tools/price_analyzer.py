"""
Airbnb price analyzer tool
"""

import json
import logging
import re
from typing import Optional, List
from datetime import datetime

from .search import airbnb_search

logger = logging.getLogger(__name__)


async def airbnb_price_analyzer(location: str, adults: int = 1, children: int = 0,
                                date_ranges: Optional[List[dict]] = None) -> str:
    """
    Analyze and compare prices across different dates for the same location
    date_ranges format: [{"checkin": "YYYY-MM-DD", "checkout": "YYYY-MM-DD"}, ...]
    """

    if not date_ranges or len(date_ranges) == 0:
        return json.dumps({
            'error': 'Please provide at least one date range to analyze',
            'format': 'date_ranges: [{"checkin": "2025-10-05", "checkout": "2025-10-07"}]'
        }, indent=2)

    try:
        logger.info(f"Analyzing prices for {location} across {len(date_ranges)} date ranges")

        all_results = []

        for idx, date_range in enumerate(date_ranges):
            checkin = date_range.get('checkin')
            checkout = date_range.get('checkout')

            if not checkin or not checkout:
                logger.warning(f"Skipping date range {idx}: missing checkin or checkout")
                continue

            # Perform search for this date range
            result_json = await airbnb_search(location, checkin, checkout, adults, children, limit=20)
            result = json.loads(result_json)

            if 'error' in result:
                logger.warning(f"Error for date range {checkin} to {checkout}: {result['error']}")
                continue

            # Calculate date range details
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
            nights = (checkout_date - checkin_date).days

            # Extract prices
            listings = result.get('searchResults', [])
            prices = []

            for listing in listings:
                price_info = listing.get('structuredDisplayPrice', {}).get('primaryLine', {})
                discounted_price = price_info.get('discountedPrice', '')
                original_price = price_info.get('originalPrice', '')

                # Extract numeric price
                if discounted_price:
                    price_match = re.search(r'[\d,]+', discounted_price.replace(',', ''))
                    if price_match:
                        total_price = float(price_match.group().replace(',', ''))
                        per_night = total_price / nights if nights > 0 else total_price

                        discount_pct = 0
                        if original_price:
                            orig_match = re.search(r'[\d,]+', original_price.replace(',', ''))
                            if orig_match:
                                orig_total = float(orig_match.group().replace(',', ''))
                                discount_pct = ((orig_total - total_price) / orig_total * 100) if orig_total > 0 else 0

                        prices.append({
                            'total': total_price,
                            'per_night': per_night,
                            'discount_percent': round(discount_pct, 1),
                            'listing_id': listing.get('id'),
                            'name': listing.get('title', 'Unknown')
                        })

            if prices:
                avg_total = sum(p['total'] for p in prices) / len(prices)
                avg_per_night = sum(p['per_night'] for p in prices) / len(prices)
                min_price = min(prices, key=lambda x: x['total'])
                max_price = max(prices, key=lambda x: x['total'])
                avg_discount = sum(p['discount_percent'] for p in prices) / len(prices)

                all_results.append({
                    'checkin': checkin,
                    'checkout': checkout,
                    'nights': nights,
                    'listings_found': len(prices),
                    'average_total_price': round(avg_total, 2),
                    'average_per_night': round(avg_per_night, 2),
                    'cheapest': {
                        'total': min_price['total'],
                        'per_night': round(min_price['per_night'], 2),
                        'listing_id': min_price['listing_id'],
                        'name': min_price['name']
                    },
                    'most_expensive': {
                        'total': max_price['total'],
                        'per_night': round(max_price['per_night'], 2),
                        'listing_id': max_price['listing_id'],
                        'name': max_price['name']
                    },
                    'average_discount_percent': round(avg_discount, 1),
                    'price_range': {
                        'min': min_price['total'],
                        'max': max_price['total']
                    }
                })

        if not all_results:
            return json.dumps({
                'error': 'No price data found for any date ranges',
                'location': location
            }, indent=2)

        # Find best value dates
        best_value = min(all_results, key=lambda x: x['average_per_night'])
        cheapest_total = min(all_results, key=lambda x: x['cheapest']['total'])
        highest_discount = max(all_results, key=lambda x: x['average_discount_percent'])

        logger.info(f"Price analysis complete for {len(all_results)} date ranges")

        return json.dumps({
            'location': location,
            'adults': adults,
            'children': children,
            'date_ranges_analyzed': len(all_results),
            'results': all_results,
            'recommendations': {
                'best_value_dates': {
                    'checkin': best_value['checkin'],
                    'checkout': best_value['checkout'],
                    'avg_per_night': best_value['average_per_night'],
                    'reason': 'Lowest average price per night'
                },
                'cheapest_overall': {
                    'checkin': cheapest_total['checkin'],
                    'checkout': cheapest_total['checkout'],
                    'cheapest_listing': cheapest_total['cheapest'],
                    'reason': 'Absolute cheapest listing found'
                },
                'best_discounts': {
                    'checkin': highest_discount['checkin'],
                    'checkout': highest_discount['checkout'],
                    'avg_discount': highest_discount['average_discount_percent'],
                    'reason': 'Highest average discount percentage'
                }
            }
        }, indent=2)

    except Exception as e:
        logger.error(f"Price analyzer failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({
            'error': str(e),
            'location': location
        }, indent=2)
