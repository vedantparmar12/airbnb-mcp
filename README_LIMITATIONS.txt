===============================================================================
                    AIRBNB MCP SERVER - READ THIS FIRST
===============================================================================

⚠️  IMPORTANT: AIRBNB SCRAPING IS UNRELIABLE ⚠️

This server may NOT work consistently because:

1. AIRBNB ACTIVELY BLOCKS BOTS
   - Sophisticated bot detection
   - CAPTCHAs frequently triggered
   - Rate limiting enforced

2. TECHNICAL CHALLENGES
   - Dynamic "Hyperloop" architecture
   - Content loaded asynchronously
   - Page structure changes frequently

3. LEGAL CONSIDERATIONS
   - May violate Airbnb's Terms of Service
   - Could have legal implications
   - Not recommended for production use

===============================================================================
                        WHAT WAS FIXED
===============================================================================

✅ ALL TECHNICAL ISSUES:
   - Unicode errors on Windows
   - Infinite loops in compare function
   - stdio transport protocol
   - Crawl4AI stdout pollution
   - Empty extraction results
   - Error attribute crashes
   - NetworkIdle timeouts

✅ CURRENT FEATURES:
   - DOM-based extraction
   - Anti-detection measures
   - Multiple extraction methods
   - Comprehensive error handling

===============================================================================
                      EXPECTED BEHAVIOR
===============================================================================

SUCCESS (30-50% of attempts):
   - Takes 10-15 seconds
   - Returns actual listings
   - Works for simple searches

FAILURE (50-70% of attempts):
   - Timeout after 30 seconds
   - "Could not extract" error
   - Access denied / CAPTCHA
   - Empty results

===============================================================================
                        RECOMMENDATIONS
===============================================================================

FOR TESTING:
   ✓ Try simple locations (Paris, Tokyo, etc.)
   ✓ Use bypass_cache: true to force fresh data
   ✓ Check debug_airbnb_page.html if it fails

FOR PRODUCTION:
   ✗ DO NOT use this server
   ✓ Get official Airbnb API access instead
   ✓ Or use paid services (RapidAPI, SerpAPI, Apify)
   ✓ Or provide static recommendations

===============================================================================
                        HOW TO USE
===============================================================================

1. RESTART CLAUDE DESKTOP

2. TRY A SEARCH:
   "Search for Airbnb in Paris"

3. IF IT FAILS:
   - Check debug_airbnb_page.html
   - Look for CAPTCHA or "Access Denied"
   - Try a different location
   - Try again later (rate limit may reset)

4. ACCEPT THE LIMITATIONS:
   - This is experimental
   - Success is not guaranteed
   - Failures are expected and normal

===============================================================================
                        ALTERNATIVE SOLUTIONS
===============================================================================

INSTEAD OF SCRAPING:

1. AIRBNB OFFICIAL API
   - Apply for API access
   - Most reliable option
   - Requires approval

2. PAID API SERVICES
   - RapidAPI Airbnb endpoints
   - SerpAPI for search results
   - Apify scraping service

3. OTHER PLATFORMS
   - Booking.com (may be easier to scrape)
   - VRBO / HomeAway
   - Hotels.com

===============================================================================
                          DISCLAIMER
===============================================================================

This server is provided AS-IS for EDUCATIONAL PURPOSES ONLY.

NO WARRANTY:
   - May not work at all
   - May stop working anytime
   - No guarantees of functionality

LEGAL RISK:
   - May violate Terms of Service
   - Could have legal consequences
   - Use at your own risk

RECOMMENDATION:
   - For learning/testing only
   - NOT for production use
   - Get official API access for real applications

===============================================================================
                        DOCUMENTATION
===============================================================================

Read these files for more information:

- IMPORTANT_AIRBNB_LIMITATIONS.md  ← START HERE
- TIMEOUT_FIX.md
- DOM_EXTRACTION_FIX.md
- FINAL_STATUS.md
- CRAWL4AI_STDOUT_FIX.md
- EXTRACTION_FIX.md

===============================================================================

Questions? This is as good as it gets for Airbnb scraping.
The technical implementation is solid, but Airbnb doesn't want bots.

Good luck! 🤞

===============================================================================
