"""
Airbnb trip budget calculator tool
"""

import json
import logging
import re
from typing import Optional
from datetime import datetime

from .search import airbnb_search
from .listing_details import airbnb_listing_details

logger = logging.getLogger(__name__)


async def airbnb_trip_budget(listing_id: str, checkin: str, checkout: str,
                             adults: int = 1, children: int = 0,
                             currency: str = "INR") -> str:
    """Calculate comprehensive trip budget including all fees and taxes"""

    try:
        logger.info(f"Calculating trip budget for listing {listing_id}")

        # Fetch listing with dates to get accurate pricing
        search_location = "India"  # Fallback location
        search_result_json = await airbnb_search(search_location, checkin, checkout, adults, children, limit=50)
        search_result = json.loads(search_result_json)

        # Find the specific listing in results
        listing = None
        for item in search_result.get('searchResults', []):
            if item.get('id') == listing_id:
                listing = item
                break

        if not listing:
            # Try to get details directly
            details_json = await airbnb_listing_details(listing_id, checkin, checkout, adults, children)
            details = json.loads(details_json)

            return json.dumps({
                'error': 'Could not find pricing information for this listing',
                'suggestion': 'Try searching for the location first, then use the listing ID from results',
                'listing_id': listing_id,
                'listing_url': details.get('listingUrl', f"https://www.airbnb.com/rooms/{listing_id}")
            }, indent=2)

        # Calculate nights
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
        nights = (checkout_date - checkin_date).days

        if nights <= 0:
            return json.dumps({
                'error': 'Checkout date must be after checkin date',
                'checkin': checkin,
                'checkout': checkout
            }, indent=2)

        # Extract price information
        price_info = listing.get('structuredDisplayPrice', {}).get('primaryLine', {})
        discounted_price_str = price_info.get('discountedPrice', '')
        original_price_str = price_info.get('originalPrice', '')

        # Parse total accommodation cost
        total_accommodation = 0
        if discounted_price_str:
            price_match = re.search(r'[\d,]+', discounted_price_str.replace(',', ''))
            if price_match:
                total_accommodation = float(price_match.group().replace(',', ''))

        if total_accommodation == 0:
            return json.dumps({
                'error': 'Could not extract pricing information',
                'listing_id': listing_id
            }, indent=2)

        # Calculate breakdown
        per_night_rate = total_accommodation / nights

        # Airbnb fees (typical percentages)
        service_fee_rate = 0.14  # ~14% service fee
        service_fee = total_accommodation * service_fee_rate

        # Tax (varies by location, using common rate)
        tax_rate = 0.12  # ~12% GST in India
        tax_amount = total_accommodation * tax_rate

        # Optional: Cleaning fee (estimate)
        cleaning_fee = per_night_rate * 0.3  # Typically 30% of one night

        # Total cost
        total_before_fees = total_accommodation
        total_with_fees = total_accommodation + service_fee + tax_amount + cleaning_fee

        # Per person breakdown
        total_guests = adults + children
        per_person_cost = total_with_fees / total_guests if total_guests > 0 else total_with_fees
        per_person_per_night = per_person_cost / nights

        # Check for discounts
        savings = 0
        discount_pct = 0
        if original_price_str:
            orig_match = re.search(r'[\d,]+', original_price_str.replace(',', ''))
            if orig_match:
                original_total = float(orig_match.group().replace(',', ''))
                savings = original_total - total_accommodation
                discount_pct = (savings / original_total * 100) if original_total > 0 else 0

        # Find cheaper alternatives in same location
        all_listings = search_result.get('searchResults', [])[:10]
        cheaper_alternatives = []

        for alt in all_listings:
            if alt.get('id') == listing_id:
                continue

            alt_price_info = alt.get('structuredDisplayPrice', {}).get('primaryLine', {})
            alt_price_str = alt_price_info.get('discountedPrice', '')

            if alt_price_str:
                alt_match = re.search(r'[\d,]+', alt_price_str.replace(',', ''))
                if alt_match:
                    alt_price = float(alt_match.group().replace(',', ''))
                    if alt_price < total_accommodation:
                        potential_savings = total_accommodation - alt_price
                        cheaper_alternatives.append({
                            'id': alt.get('id'),
                            'name': alt.get('title', 'Unknown'),
                            'url': alt.get('url'),
                            'price': alt_price,
                            'savings': round(potential_savings, 2),
                            'rating': alt.get('avgRatingLocalized', 'N/A')
                        })

        # Sort by savings
        cheaper_alternatives.sort(key=lambda x: x['savings'], reverse=True)

        logger.info(f"Budget calculation complete for listing {listing_id}")

        return json.dumps({
            'listing_id': listing_id,
            'listing_name': listing.get('title', 'Unknown'),
            'listing_url': listing.get('url'),
            'dates': {
                'checkin': checkin,
                'checkout': checkout,
                'nights': nights
            },
            'guests': {
                'adults': adults,
                'children': children,
                'total': total_guests
            },
            'cost_breakdown': {
                'accommodation_total': round(total_accommodation, 2),
                'per_night_rate': round(per_night_rate, 2),
                'service_fee_14pct': round(service_fee, 2),
                'tax_12pct': round(tax_amount, 2),
                'cleaning_fee_estimate': round(cleaning_fee, 2),
                'currency': currency
            },
            'total_cost': {
                'before_fees': round(total_before_fees, 2),
                'with_all_fees': round(total_with_fees, 2),
                'currency': currency
            },
            'per_person': {
                'total': round(per_person_cost, 2),
                'per_night': round(per_person_per_night, 2),
                'currency': currency
            },
            'savings': {
                'discount_amount': round(savings, 2) if savings > 0 else 0,
                'discount_percent': round(discount_pct, 1) if savings > 0 else 0
            },
            'cheaper_alternatives': cheaper_alternatives[:3],  # Top 3
            'note': 'Service fee, tax, and cleaning fee are estimates. Actual amounts may vary at checkout.'
        }, indent=2)

    except Exception as e:
        logger.error(f"Trip budget calculation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return json.dumps({
            'error': str(e),
            'listing_id': listing_id
        }, indent=2)
