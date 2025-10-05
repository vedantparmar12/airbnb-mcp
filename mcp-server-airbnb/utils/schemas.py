"""
Data schemas for filtering Airbnb API responses
"""


def get_search_result_schema():
    """Schema for filtering search results"""
    return {
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


def get_listing_details_schema():
    """Schema for filtering listing details sections"""
    return {
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
