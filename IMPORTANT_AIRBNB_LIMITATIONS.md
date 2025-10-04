# Important: Airbnb Scraping Limitations

## Reality Check ⚠️

**Airbnb actively works to prevent automated scraping.** This MCP server may experience frequent failures due to:

### 1. Bot Detection
- Airbnb uses sophisticated bot detection
- Headless browsers are often blocked
- CAPTCHAs may be triggered
- Rate limiting applies

### 2. Dynamic Architecture
- "Hyperloop" architecture with async data loading
- Content loaded via JavaScript after initial page load
- Page never reaches "networkidle" state
- Continuous background requests for analytics/tracking

### 3. Frequent Changes
- Airbnb updates their website structure regularly
- CSS selectors and data attributes change
- Script tag formats evolve
- API endpoints are not public

## Current Fixes Applied

✅ **Wait strategy**: Changed from `networkidle` to `load`  
✅ **Anti-detection**: Browser flags to hide automation  
✅ **Multiple extraction methods**: JSON + DOM scraping  
✅ **Extended waits**: 7 seconds total for content to render  
✅ **Error handling**: Graceful failures with debug output  

## Expected Success Rate

- **Fresh deployment**: ~30-50% success rate
- **After Airbnb updates**: May drop to 0%
- **With rate limiting**: Decreases over time
- **Geographic restrictions**: Varies by location

## When It Works

✅ First few requests  
✅ Simple searches (e.g., "Paris")  
✅ When Airbnb hasn't updated recently  
✅ With good network conditions  

## When It Fails

❌ After multiple requests (rate limiting)  
❌ From certain IPs/regions  
❌ When CAPTCHA is triggered  
❌ After Airbnb updates their site  
❌ With complex search parameters  

## Typical Errors

### 1. Timeout (60s)
```
Page.goto: Timeout 60000ms exceeded
waiting until "networkidle"
```
**Cause**: Page never reaches idle state  
**Fix**: Already applied (use "load" instead)

### 2. Empty Results
```
Could not find __NEXT_DATA__ or initial-data script tag
```
**Cause**: Airbnb changed data format  
**Fix**: DOM scraping should work (already implemented)

### 3. Access Denied
```
403 Forbidden or CAPTCHA page
```
**Cause**: Bot detected  
**Fix**: Can't be fully solved without proxy/API

## Alternatives

### 1. Official Airbnb API
- **Pros**: Reliable, fast, no scraping needed
- **Cons**: Requires approval, not publicly available

### 2. Proxy Service
- **Pros**: Better success rate, rotates IPs
- **Cons**: Costs money, setup complexity

### 3. Manual Search
- **Pros**: Always works
- **Cons**: Not automated

### 4. Static Recommendations
- **Pros**: Instant, no scraping
- **Cons**: Not real-time data

## Recommendations

### For Testing
```python
# Try simple locations first
"Search for Airbnb in Paris"
"Find listings in Tokyo"
```

### For Production Use
1. **Use Airbnb API** if available
2. **Implement proxy rotation** for scraping
3. **Add caching** to reduce requests
4. **Provide fallback data** when scraping fails
5. **Consider alternatives** (Booking.com, VRBO, etc.)

## Current Server Behavior

### On Success (rare)
```
1. Load page (~3-5s)
2. Wait for rendering (~5-7s)
3. Try JSON extraction
4. Fall back to DOM scraping
5. Return listings
Total: ~10-15 seconds
```

### On Failure (common)
```
1. Attempt to load page
2. Timeout or get blocked
3. Return error with debug info
4. Save debug HTML file
Total: 10-30 seconds
```

## Debug Information

When extraction fails, check:

1. **Debug file**: `debug_airbnb_page.html`
   - Look for CAPTCHA page
   - Search for "Access Denied"
   - Check if listings appear in HTML

2. **Logs** (stderr):
   ```
   ERROR - Could not find valid script tags
   ERROR - DOM extraction failed
   ERROR - All extraction methods failed
   ```

3. **Try manually**:
   - Open the URL in a browser
   - See if you can access the page
   - Check for CAPTCHA or blocking

## Legal & Ethical Considerations

⚠️ **Important**: Web scraping may violate:
- Airbnb's Terms of Service
- Computer Fraud and Abuse Act (CFAA)
- GDPR and privacy regulations
- Local laws in your jurisdiction

**Recommendation**: 
- Use this server for **educational purposes** only
- For production use, get official API access
- Respect robots.txt and rate limits
- Don't scrape personal data

## Disclaimer

This MCP server is provided **AS-IS** with no guarantees of:
- Functionality
- Reliability
- Legal compliance
- Data accuracy

**Use at your own risk.**

## Better Alternatives for Production

### 1. RapidAPI Airbnb Data
- Paid API service
- Reliable and legal
- Good success rate

### 2. SerpAPI
- Google search results for Airbnb
- More reliable than direct scraping
- Paid service

### 3. Apify
- Professional scraping service
- Handles anti-bot measures
- Costs money

### 4. Official Partnerships
- Apply for Airbnb affiliate program
- Get access to official data
- Most reliable option

## Conclusion

**This MCP server is experimental and may not work reliably with Airbnb.**

For demonstration and testing purposes only. For production use cases requiring reliable Airbnb data, please use official APIs or paid services.

The server implements best practices for scraping (respects robots.txt by default, proper error handling, rate limiting awareness) but cannot overcome Airbnb's anti-scraping measures completely.

---

**Status**: ⚠️ Experimental  
**Reliability**: 🟡 Low to Medium  
**Recommendation**: 🔴 Not for production without official API  
