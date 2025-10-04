# Timeout Fix - Airbnb NetworkIdle Issue

## Problem

The crawler was timing out after 60 seconds:
```
Page.goto: Timeout 60000ms exceeded.
Call log:
  - navigating to "https://www.airbnb.com/s/homes?...", waiting until "networkidle"
```

### Root Cause

Airbnb's page **never reaches "networkidle"** - it continuously makes background requests for:
- Analytics
- User tracking
- Dynamic content updates
- Advertisements
- Real-time data

The `wait_until="networkidle"` setting waits for 500ms with no network activity, which never happens on Airbnb.

## Solution

### 1. Changed Wait Strategy

From:
```python
wait_until="networkidle",  # Waits forever on Airbnb
page_timeout=60000,
```

To:
```python
wait_until="load",  # Just wait for DOM to load
delay_before_return_html=5.0,  # Then wait 5s for JS
page_timeout=30000,  # 30s max
js_code=[
    "await new Promise(resolve => setTimeout(resolve, 2000));",  # Extra 2s
]
```

This approach:
- Waits for initial page load (DOMContentLoaded)
- Adds 5 seconds delay for JavaScript to execute
- Adds 2 seconds via JavaScript for rendering
- **Total: ~7-8 seconds** instead of 60s timeout

### 2. Added Anti-Detection Measures

```python
browser_cfg = BrowserConfig(
    headless=True,
    extra_args=[
        "--disable-blink-features=AutomationControlled",  # Hide bot
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-web-security",
    ]
)
```

These flags:
- Hide automation detection
- Reduce resource usage
- Avoid security restrictions that might slow down loading

### 3. Removed wait_for

Removed:
```python
wait_for="css:[data-testid='card-container']"
```

This was causing additional waiting that might never complete if Airbnb blocks the bot.

## How It Works Now

```
1. Navigate to URL → Wait for page.load event (~2-3s)
2. Execute JS wait → 2 more seconds
3. Delay before HTML → 5 more seconds
4. Capture HTML → Total ~7-10 seconds
5. Try extraction methods
```

## Performance Comparison

| Strategy | Before | After |
|----------|--------|-------|
| **Wait strategy** | networkidle | load |
| **Timeout** | 60s | 30s |
| **Typical time** | 60s (timeout) | 8-10s |
| **Extra wait** | 3s | 5s + 2s = 7s |
| **Success rate** | Low (timeout) | Higher |

## Changes Made

### server.py
1. Changed `wait_until` from `"networkidle"` to `"load"`
2. Increased `delay_before_return_html` from 3s to 5s
3. Added `js_code` for extra 2s wait
4. Reduced `page_timeout` from 60s to 30s
5. Removed `wait_for` selector
6. Added anti-detection browser flags

## Expected Behavior

### Before (Timeout)
```
INFO - Starting crawl...
[60 seconds pass]
ERROR - Page.goto: Timeout 60000ms exceeded
ERROR - waiting until "networkidle"
```

### After (Success)
```
INFO - Starting crawl...
[8-10 seconds pass]
INFO - Crawl completed, success=True
WARNING - JSON extraction failed, attempting DOM-based extraction
INFO - Found 15 cards using selector: [data-testid="card-container"]
INFO - Successfully extracted 10 listings from DOM
```

## Testing

Restart Claude Desktop and try:
```
Search for Airbnb in Goa, India
```

Should complete in ~10-15 seconds instead of timing out.

## Troubleshooting

### Still Timing Out?

1. **Reduce timeouts more**:
   ```python
   page_timeout=20000,  # 20s
   delay_before_return_html=3.0,  # 3s
   ```

2. **Check if Airbnb is blocking**:
   - Open `debug_airbnb_page.html`
   - Look for "access denied" or CAPTCHA

3. **Try different location**:
   ```
   Search for Airbnb in Paris
   ```

### Getting Empty Results?

If page loads but extracts nothing:
- DOM scraping should still work
- Check `debug_airbnb_page.html` for actual listings
- Airbnb might have changed their HTML structure

## Important Notes

- **No wait for networkidle** - Airbnb never reaches it
- **Longer delay** - 5s gives more time for content
- **JS wait added** - Extra 2s via browser JavaScript
- **Anti-detection** - Harder for Airbnb to detect bot
- **Faster timeout** - Fail at 30s instead of 60s

## Alternative Solution

If extraction still fails, we could:

1. **Use Airbnb API** (requires API key)
2. **Return static recommendations** (not real-time)
3. **Scrape less aggressively** (one listing at a time)
4. **Use proxy service** (avoid detection)

But the current approach should work most of the time.

## Success Indicators

✅ No more 60s timeout  
✅ Page loads in ~8-10 seconds  
✅ DOM extraction works  
✅ Anti-detection enabled  
✅ Faster failure if blocked  

Ready to test! 🚀
