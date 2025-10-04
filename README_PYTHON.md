# Airbnb MCP Server - Python FastMCP Enhanced Edition

A powerful Python-based MCP server for Airbnb search and listing operations with enhanced features including caching, image extraction, review analysis, price calculation, and listing comparison.

## New Features (Python Version)

### Enhanced over TypeScript version:
- **Crawl4AI Powered**: Uses the advanced `Crawl4AI` library for robust, efficient, and resilient web scraping.
- **Smart Caching**: Leverages `Crawl4AI`'s built-in, configurable caching (`ENABLED`, `DISABLED`, `BYPASS`).
- **Image Extraction**: Automatically extracts property images during search.
- **Parallel Comparisons**: Fetches multiple listings concurrently for fast side-by-side comparisons.
- **Cache Management**: Provides a tool to clear the entire `Crawl4AI` cache directory.
- **Fully Asynchronous**: Built from the ground up with `async/await`.
- **Structured Data Extraction**: Uses Pydantic models and `Crawl4AI`'s extraction strategies for reliable data parsing.

## Tools

### 1. `airbnb_search`
Search for Airbnb listings with comprehensive filtering.

**Parameters:**
- `location` (required): Location to search (e.g., 'Paris, France').
- `checkin` (optional): Check-in date (YYYY-MM-DD).
- `checkout` (optional): Checkout date (YYYY-MM-DD).
- `guests` (optional): Number of guests.
- `limit` (optional): Number of results to return.
- `ignoreRobotsText` (optional): Override robots.txt compliance.
- `bypass_cache` (optional): Force a fresh search, ignoring any cached data.

**Returns:**
- A JSON list of listings including ID, name, price, and image.

### 2. `airbnb_listing_details`
Get comprehensive listing information.

**Parameters:**
- `id` (required): The ID of the listing.
- `ignoreRobotsText` (optional): Override robots.txt compliance.
- `bypass_cache` (optional): Force a fresh fetch, ignoring any cached data.

**Returns:**
- Detailed property information including name, description, and capacity.

### 3. `airbnb_compare_listings` (New)
Compare multiple listings side-by-side.

**Parameters:**
- `ids` (required): A list of up to 5 listing IDs.

**Returns:**
- A JSON list containing the detailed information for each requested listing.

### 4. `clear_cache` (New)
Clear the `Crawl4AI` cache.

**Returns:**
- A confirmation message indicating the result.

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "airbnb-enhanced": {
      "command": "python",
      "args": [
        "/path/to/server.py"
      ]
    }
  }
}
```

### For Cursor/VS Code

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "airbnb-enhanced": {
      "command": "python",
      "args": [
        "C:\\Users\\vedan\\Desktop\\mcp-rag\\travel-agent-system\\airbnb\\mcp-server-airbnb\\server.py"
      ]
    }
  }
}
```

## Usage Examples

### Basic Search
```python
# Search for listings in San Francisco
airbnb_search(
    location="San Francisco, CA",
    checkin="2025-11-01",
    checkout="2025-11-05",
    guests=2
)
```

### Get Listing Details
```python
# Get detailed info about a specific listing
airbnb_listing_details(
    id="12345678"
)
```

### Compare Multiple Listings
```python
# Compare 3 listings
airbnb_compare_listings(
    ids=["12345678", "87654321", "11223344"]
)
```

## Architecture

### Tech Stack
- **FastMCP**: Modern Python MCP framework.
- **Crawl4AI**: Advanced, AI-powered web crawler and scraper.
- **Pydantic**: Data validation and structured data modeling.

### Caching Strategy
- Powered by `Crawl4AI`'s built-in file-based caching system.
- Configurable per-request via `CacheMode` (`ENABLED`, `DISABLED`, `BYPASS`).
- Manual cache clearing available via the `clear_cache` tool.

### Error Handling
- Handled by `Crawl4AI`'s robust retry and error management system.
- Detailed error logging for failed scrapes.
- User-friendly error messages returned in the JSON response.

## Security & Compliance

- Robots.txt compliance (configurable via `--ignore-robots-txt` flag).
- Request timeouts managed by `Crawl4AI`.
- Standard `User-Agent` to identify traffic.

## Performance

- Fully asynchronous (`async/await`) implementation.
- Parallel fetching of multiple pages using `asyncio.gather` for comparisons.
- Efficient data extraction using `Crawl4AI`'s `JsonCssExtractionStrategy`.
- Significant speed-up on repeated requests thanks to `Crawl4AI`'s caching.

## Comparison: Python vs TypeScript

| Feature | TypeScript | Python (Enhanced) |
|---------|-----------|-------------------|
| **Scraping Engine** | `axios` | **`Crawl4AI`** |
| Search | [OK] | [OK] |
| Listing Details | [OK] | [OK] |
| **Caching** | [NO] | [OK] (Built-in) |
| **Parallel Scraping**| [NO] | [OK] |
| Comparison Tool | [NO] | [OK] |
| Cache Management | [NO] | [OK] |
| Type Safety | [OK] (TypeScript) | [OK] (Pydantic) |
| Async | [NO] (Partial) | [OK] (Full) |

## Troubleshooting

### Page Structure Changed Error
- Airbnb occasionally updates their HTML structure
- Check the script tag ID in the source
- Update the extraction logic if needed

### Cache Issues
- Use `clear_cache` tool to reset

### Timeout Errors
- Check network connectivity
- Verify Airbnb accessibility

## Contributing

Contributions welcome! Areas for improvement:
- GraphQL API integration (more efficient)
- Redis caching backend
- More accurate price calculations
- Additional filters (room types, amenities)
- Export to CSV/JSON
- Rate limiting implementation

## License

MIT License - Same as original TypeScript version

## Credits

- Original TypeScript implementation by OpenBnB
- Enhanced Python version with FastMCP
- Built on Model Context Protocol

## Disclaimer

This tool is for legitimate research and booking assistance only. Respect Airbnb's Terms of Service and robots.txt. Not affiliated with Airbnb, Inc.
