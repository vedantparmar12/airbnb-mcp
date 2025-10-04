# Airbnb Extraction Fix - Empty Results Issue

## Problem

The server was connecting successfully but returning empty results:

```
2025-10-05 02:02:44,240 - INFO - Extraction result: success=True, has_content=True
2025-10-05 02:02:44,240 - ERROR - Extracted data structure: []
2025-10-05 02:02:44,241 - ERROR - Error during Airbnb search: Could not find script_content in extracted data.
```

The extraction was "successful" but returned an empty array `[]` instead of actual data.

## Root Causes

1. **Empty Array is Truthy**: `[]` evaluates to `True` in Python, so the fallback HTML parsing never ran
2. **CSS Selector Not Matching**: The JsonCssExtractionStrategy couldn't find the script tags
3. **JavaScript Not Executing**: Airbnb is a React app that needs JavaScript to render __NEXT_DATA__
4. **Page Not Fully Loaded**: Script tags appear after JS execution completes

## Solutions Applied

### 1. Fixed Empty Array Handling

Changed from:
```python
if not result.extracted_content:
    # Fallback never ran because [] is truthy!
```

To:
```python
extraction_failed = False
try:
    if result.extracted_content:
        extracted_list = json.loads(result.extracted_content) if isinstance(result.extracted_content, str) else result.extracted_content
        
        # Check if we got valid data (not just empty array)
        if extracted_list and isinstance(extracted_list, list) and len(extracted_list) > 0:
            if 'script_content' in extracted_list[0] and extracted_list[0]['script_content']:
                # Process valid data
                ...
        
        # Empty or malformed - flag for fallback
        extraction_failed = True
except Exception as e:
    extraction_failed = True

# Now fallback runs when needed
if extraction_failed:
    # HTML fallback parsing
```

### 2. Improved CSS Selector

Updated selector to be more flexible:
```python
schema = {
    "name": "GetNextData",
    "baseSelector": "html",  # Changed from "body"
    "fields": [{
        "name": "script_content",
        # Multiple selectors to try
        "selector": "script#__NEXT_DATA__, script#initial-data, script[type='application/json']",
        "type": "text",
        "all": False
    }]
}
```

### 3. Enabled JavaScript Execution

```python
browser_cfg = BrowserConfig(
    user_agent=USER_AGENT,
    headless=True,
    verbose=False,
    accept_downloads=False,
    java_script_enabled=True  # NEW: Enable JS for React apps
)
```

### 4. Wait for Page Load

```python
config = CrawlerRunConfig(
    extraction_strategy=strategy,
    cache_mode=cache_mode,
    verbose=False,
    word_count_threshold=1,
    only_text=False,
    wait_until="networkidle",  # NEW: Wait for network idle
    delay_before_return_html=2.0,  # NEW: Extra 2s delay for JS
    page_timeout=60000  # NEW: 60s timeout
)
```

### 5. Enhanced HTML Fallback Parsing

Multiple regex patterns to handle different script tag formats:
```python
patterns = [
    r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
    r'<script[^>]*id=["\']initial-data["\'][^>]*>(.*?)</script>',
    r'<script[^>]*type=["\']application/json["\'][^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
]

for pattern in patterns:
    matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
    if matches:
        try:
            json_data = json.loads(matches[0])
            return json_data.get('props', {}).get('pageProps', {})
        except json.JSONDecodeError:
            continue  # Try next pattern
```

### 6. Debug Output

When extraction fails, save HTML to file:
```python
# Save HTML to file for debugging
debug_file = "debug_airbnb_page.html"
try:
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.error(f"Saved full HTML to {debug_file} for debugging")
except Exception as e:
    logger.error(f"Could not save debug HTML: {e}")
```

## Configuration Changes

### Browser Configuration
- ✅ Enabled JavaScript execution
- ✅ Set proper user agent
- ✅ Disabled verbose output

### Crawler Configuration
- ✅ Wait for network idle (JS loaded)
- ✅ 2-second delay before capturing HTML
- ✅ 60-second page timeout
- ✅ Keep full HTML (not just text)

### Extraction Strategy
- ✅ Multiple CSS selectors
- ✅ HTML fallback parsing
- ✅ Multiple regex patterns

## Testing

After fixes, test with:
```bash
python test_server_startup.py
# Should show: [OK] Server started successfully!
```

Then restart Claude Desktop and try:
```
Search for Airbnb listings in Goa, India
```

## Expected Behavior

### Before Fix
```
ERROR - Extracted data structure: []
ERROR - Error during Airbnb search: Could not find script_content in extracted data.
```

### After Fix
```
INFO - Extraction result: success=True, has_content=True
INFO - Successfully extracted data using HTML fallback
# Returns actual listing data
```

Or if HTML fallback is used:
```
INFO - Attempting HTML fallback parsing
INFO - Successfully extracted data using HTML fallback
```

## Debugging

If extraction still fails:

1. **Check debug file**: Look at `debug_airbnb_page.html` in the project directory
2. **Search for script tags**: Look for `<script id="__NEXT_DATA__"` or `<script id="initial-data"`
3. **Check for anti-bot**: Airbnb might be detecting the crawler
4. **Increase delay**: Try `delay_before_return_html=5.0` for slower page load

## Important Notes

- **No .env file needed** - all configuration is in code
- **JavaScript execution is critical** - Airbnb won't work without it
- **Fallback is essential** - CSS extraction is unreliable
- **Debug file helps** - Check `debug_airbnb_page.html` when extraction fails

## Key Differences from Before

| Aspect | Before | After |
|--------|--------|-------|
| **Empty array check** | `if not result.extracted_content` ❌ | Check length and content ✅ |
| **JavaScript** | Not configured | Enabled ✅ |
| **Page wait** | None | networkidle + 2s delay ✅ |
| **Fallback** | Single pattern | Multiple patterns ✅ |
| **Debug** | Log only | Save HTML file ✅ |

## Related Files

- `server.py` - All fixes applied here
- `test_extraction.py` - Quick test script
- `debug_airbnb_page.html` - Generated when extraction fails

## Success Indicators

✅ Server starts without errors  
✅ No stdout pollution (JSON-RPC clean)  
✅ JavaScript enabled in browser config  
✅ Page waits for network idle  
✅ HTML fallback parsing works  
✅ Debug file created on failure  
✅ Multiple regex patterns tried  
