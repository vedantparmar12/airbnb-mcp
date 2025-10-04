# Airbnb MCP Server - Python Implementation

A Python-based MCP (Model Context Protocol) server for searching Airbnb listings and retrieving detailed property information. Uses Crawl4AI for web scraping and the official MCP SDK for stdio transport.

## Features

- **Search Airbnb Listings**: Search by location, dates, guests, and more
- **Get Listing Details**: Retrieve comprehensive information about specific properties
- **Compare Listings**: Compare up to 5 listings side-by-side
- **Cache Management**: Clear the Crawl4AI cache when needed
- **Robots.txt Compliance**: Respects robots.txt by default (can be disabled for testing)
- **Windows Compatible**: Fixed unicode encoding issues for Windows consoles

## Requirements

- Python 3.12 or higher
- Required packages (see requirements.txt):
  - mcp >= 1.0.0 (Official MCP SDK)
  - crawl4ai >= 0.4.0
  - pydantic >= 2.0.0
  - lxml >= 5.0.0

## Installation

### 1. Clone or download this repository

```bash
cd mcp-server-airbnb
```

### 2. Install dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Using uv (recommended):
```bash
uv pip install -r requirements.txt
```

### 3. Test the server

```bash
python test_server_startup.py
```

You should see: `[OK] Server started successfully!`

## Usage

### Running the Server Standalone

**Standard mode (with robots.txt compliance):**
```bash
python server.py
```

**Ignore robots.txt (for testing):**
```bash
python server.py --ignore-robots-txt
```

### Configuring with MCP Clients

#### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "python",
      "args": [
        "C:\\path\\to\\mcp-server-airbnb\\server.py"
      ]
    }
  }
}
```

To ignore robots.txt:
```json
{
  "mcpServers": {
    "airbnb": {
      "command": "python",
      "args": [
        "C:\\path\\to\\mcp-server-airbnb\\server.py",
        "--ignore-robots-txt"
      ]
    }
  }
}
```

#### Cursor IDE Configuration

Go to: Cursor Settings > Tools & Integrations > New MCP Server

Add to your `mcp.json`:
```json
{
  "mcpServers": {
    "airbnb": {
      "command": "python",
      "args": [
        "/path/to/mcp-server-airbnb/server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. airbnb_search

Search for Airbnb listings with various filters.

**Parameters:**
- `location` (required): Location to search (e.g., "San Francisco, CA")
- `checkin` (optional): Check-in date in YYYY-MM-DD format
- `checkout` (optional): Check-out date in YYYY-MM-DD format
- `guests` (optional): Number of guests (default: 1)
- `limit` (optional): Number of results to return (default: 10)
- `ignoreRobotsText` (optional): Bypass robots.txt for this request
- `bypass_cache` (optional): Force fresh data fetch

**Example:**
```json
{
  "location": "Paris, France",
  "checkin": "2024-06-01",
  "checkout": "2024-06-07",
  "guests": 2,
  "limit": 5
}
```

**Returns:** JSON array of listings with id, name, city, price, url, and image_url

### 2. airbnb_listing_details

Get detailed information about a specific Airbnb listing.

**Parameters:**
- `id` (required): Airbnb listing ID
- `ignoreRobotsText` (optional): Bypass robots.txt for this request
- `bypass_cache` (optional): Force fresh data fetch

**Example:**
```json
{
  "id": "12345678"
}
```

**Returns:** JSON object with listing details including name, description, room_type, person_capacity, reviews_count, and url

### 3. airbnb_compare_listings

Compare up to 5 Airbnb listings side-by-side.

**Parameters:**
- `ids` (required): Array of listing IDs to compare (max 5)

**Example:**
```json
{
  "ids": ["12345678", "87654321", "11223344"]
}
```

**Returns:** JSON array of listing details for comparison

### 4. clear_cache

Clear the Crawl4AI cache directory.

**Parameters:** None

**Returns:** Success or error message

## Testing

### Quick Startup Test

```bash
python test_server_startup.py
```

### Full Integration Test

```bash
python test_client.py
```

This will test all available tools:
1. Initialize the MCP connection
2. Search for listings
3. Get listing details
4. Compare multiple listings
5. Clear the cache

## Architecture

### stdio Transport

The server uses the official MCP SDK with stdio transport, which means:
- Input/output via stdin/stdout
- Logging goes to stderr only
- JSON-RPC protocol for communication
- Compatible with all MCP clients

### Windows Compatibility

Fixed issues:
- UTF-8 encoding for stdout/stderr
- Unicode character handling in logs
- Console output encoding errors

### No More Loop Issues

The compare listings function now uses an internal helper function instead of recursively calling the MCP tool wrapper, preventing the 5-listing limit loop.

## Troubleshooting

### Unicode Errors on Windows

The server automatically configures UTF-8 encoding for Windows. If you still see errors, ensure you're using Python 3.12+ and the latest version of the server.

### Server Won't Start

1. Check Python version: `python --version` (must be 3.12+)
2. Check dependencies: `pip list | grep -E "mcp|crawl4ai"`
3. Check logs in stderr output

### Connection Issues

1. Ensure the server is running: `python test_server_startup.py`
2. Check MCP client configuration file path
3. Verify absolute paths in configuration
4. Check stderr logs for errors

### Cache Issues

If you're getting stale data:
1. Use the `clear_cache` tool
2. Or manually delete the `.crawl4ai_cache` directory
3. Use `bypass_cache: true` parameter in tool calls

## Development

### Project Structure

```
mcp-server-airbnb/
├── server.py                 # Main MCP server (Python)
├── server_fastmcp_backup.py  # Old FastMCP version (backup)
├── test_server_startup.py    # Quick startup test
├── test_client.py            # Full integration test
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Python project metadata
└── README_PYTHON_MCP.md     # This file
```

### Adding New Tools

1. Create the tool function in server.py
2. Add the tool definition in `list_tools()`
3. Add the handler in `call_tool()`
4. Test with test_client.py

## Known Limitations

- Airbnb's page structure may change, requiring updates
- Robots.txt may block certain paths (use `--ignore-robots-txt` for testing)
- Rate limiting by Airbnb may occur with heavy usage
- Some listings may have incomplete data

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Test your changes with `test_client.py`
2. Ensure Windows compatibility
3. Follow existing code style
4. Update documentation

## Support

- Issues: Report on GitHub
- Documentation: See this README and FIXES_APPLIED.md
- Examples: Check test_client.py for usage examples
