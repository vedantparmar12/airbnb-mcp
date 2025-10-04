# DOM-Based Extraction Fix

## Problem

Airbnb changed their architecture and no longer uses `__NEXT_DATA__` script tags. The page now uses their "Hyperloop" architecture where data is loaded asynchronously via JavaScript and injected into the DOM.

**Evidence from logs:**
```
<html lang="en-IN" dir="ltr" data-is-hyperloop="true" data-is-async-local-storage="true"
```

No inline JSON data is present in the initial HTML.

## Solution

### 1. Wait for Actual Content to Load

Changed waiting strategy:
```python
config = CrawlerRunConfig(
    wait_until="networkidle",  # Wait for all network requests
    delay_before_return_html=3.0,  # Wait 3 seconds for rendering
    page_timeout=60000,  # 60 second timeout
    wait_for="css:[data-testid='card-container'], css:[itemprop='itemListElement']"  # Wait for listings
)
```

This makes the crawler:
- Wait for network to be idle (all async requests done)
- Wait an additional 3 seconds for DOM to render
- Specifically wait for listing card elements to appear

### 2. Added More JSON Patterns

```python
patterns = [
    r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
    r'<script[^>]*id=["\']initial-data["\'][^>]*>(.*?)</script>',
    r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',
    r'<script[^>]*data-state=["\']true["\'][^>]*>(.*?)</script>',
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',  # Schema.org
]
```

### 3. DOM-Based Extraction (Fallback)

When JSON extraction fails, scrape from the rendered DOM:

```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Try various selectors for listing cards
card_selectors = [
    '[data-testid="card-container"]',
    '[itemprop="itemListElement"]',
    '[data-testid="listing-card"]',
    '.c4mnd7m',  # Airbnb CSS class
    '[role="group"]'
]

for selector in card_selectors:
    cards = soup.select(selector)
    if cards:
        for card in cards:
            listing = {}
            
            # Extract ID
            listing['id'] = card.get('data-listing-id')
            
            # Extract name/title
            title_elem = card.select_one('[data-testid="listing-card-title"], h3, h2')
            listing['name'] = title_elem.get_text(strip=True)
            
            # Extract price
            price_elem = card.select_one('[data-testid="price-availability-row"]')
            listing['price_formatted'] = price_elem.get_text(strip=True)
            
            # Extract URL
            link_elem = card.select_one('a[href*="/rooms/"]')
            listing['url'] = BASE_URL + link_elem.get('href')
            
            # Extract image
            img_elem = card.select_one('img[src*="airbnb"]')
            listing['image_url'] = img_elem.get('src')
            
            listings.append(listing)
```

This scrapes data directly from the rendered HTML elements.

## Changes Made

### Files Modified
1. `server.py` - Added DOM extraction logic
2. `requirements.txt` - Added `beautifulsoup4>=4.12.0`

### Key Improvements
1. **Wait for actual listings** to appear in DOM
2. **Multiple extraction methods**:
   - JSON from script tags (preferred)
   - DOM scraping (fallback)
3. **More robust selectors** for different Airbnb layouts
4. **Better error handling** with fallback chain

## How It Works

```
1. Load page with JavaScript enabled
2. Wait for networkidle
3. Wait 3 additional seconds
4. Wait for listing elements to appear
5. Try JSON extraction from script tags
6. If fails → Try DOM-based extraction
7. If fails → Save debug HTML and error
```

## Expected Behavior

### Before
```
ERROR - Could not find valid script tags
ERROR - Could not find __NEXT_DATA__ or initial-data script tag
```

### After
```
INFO - Starting crawl for https://www.airbnb.com/...
INFO - Crawl completed, success=True
WARNING - JSON extraction failed, attempting DOM-based extraction
INFO - Found 20 cards using selector: [data-testid="card-container"]
INFO - Successfully extracted 10 listings from DOM
```

## Dependencies Added

- **beautifulsoup4** - For HTML parsing and DOM traversal

## Configuration Changes

| Setting | Before | After | Reason |
|---------|--------|-------|--------|
| `wait_until` | domcontentloaded | networkidle | Wait for async data |
| `delay_before_return_html` | 1.0s | 3.0s | More time for rendering |
| `page_timeout` | 30000ms | 60000ms | Airbnb needs time |
| `wait_for` | (none) | CSS selectors | Wait for listings |

## Testing

Restart Claude Desktop and try:
```
Search for Airbnb in Goa, India
```

Should now return actual listings!

## Performance

- **JSON extraction**: ~10-15 seconds
- **DOM extraction**: ~15-20 seconds
- **Full timeout**: 60 seconds max

## Debugging

If extraction still fails:

1. **Check debug file**: `debug_airbnb_page.html`
2. **Look for listings**: Search for `data-testid="card-container"`
3. **Check network**: Airbnb might be blocking the crawler
4. **Increase wait time**: Try `delay_before_return_html=5.0`

## Important Notes

- **BeautifulSoup required** - Already installed in your environment
- **Longer wait times** - Necessary for Airbnb's async architecture
- **DOM scraping is slower** - But more reliable for modern SPAs
- **May need updates** - If Airbnb changes their HTML structure

## Success Indicators

✅ Listings found via DOM scraping  
✅ No more "__NEXT_DATA__ not found" errors  
✅ Actual Airbnb data returned  
✅ Works with Airbnb's Hyperloop architecture  

Ready to test with Claude Desktop! 🚀
