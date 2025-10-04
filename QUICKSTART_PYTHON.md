# Python MCP Server - Quick Start Guide

## What Was Fixed

✅ **Unicode errors on Windows** - No more `UnicodeEncodeError`  
✅ **Infinite loop in compare_listings** - Fixed recursive tool calls  
✅ **stdio transport** - Now uses proper MCP protocol  
✅ **Switched to official MCP SDK** - No more FastMCP

## Installation

```bash
cd C:\Users\vedan\Desktop\mcp-rag\travel-agent-system\airbnb\mcp-server-airbnb
pip install -r requirements.txt
```

## Test It Works

```bash
python test_server_startup.py
```

You should see: **[OK] Server started successfully!**

## Use with Claude Desktop

1. Open: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add this configuration:
```json
{
  "mcpServers": {
    "airbnb": {
      "command": "python",
      "args": [
        "C:\\Users\\vedan\\Desktop\\mcp-rag\\travel-agent-system\\airbnb\\mcp-server-airbnb\\server.py"
      ]
    }
  }
}
```

3. Restart Claude Desktop

4. Try asking Claude: "Search for Airbnb listings in Paris"

## Use with Cursor

1. Go to: **Cursor Settings > Tools & Integrations > New MCP Server**

2. Add the same configuration as above

3. Restart Cursor

## Available Tools

- **airbnb_search** - Search for listings by location
- **airbnb_listing_details** - Get details for a specific listing
- **airbnb_compare_listings** - Compare up to 5 listings
- **clear_cache** - Clear the cache

## Run Options

**Standard (respects robots.txt):**
```bash
python server.py
```

**Ignore robots.txt (for testing):**
```bash
python server.py --ignore-robots-txt
```

## Files Overview

- `server.py` - Main server (uses official MCP SDK)
- `server_fastmcp_backup.py` - Old version (backup)
- `test_server_startup.py` - Quick startup test
- `test_client.py` - Full integration test
- `README_PYTHON_MCP.md` - Full documentation
- `FIXES_APPLIED.md` - Technical details of all fixes

## Troubleshooting

**Server won't start?**
1. Check Python version: `python --version` (need 3.12+)
2. Check dependencies: `pip list | findstr /i "mcp crawl4ai"`

**Still getting unicode errors?**
- Make sure you're using the NEW `server.py` (not the backup)
- The new version has UTF-8 handling built-in

**Tools not appearing in client?**
1. Check the full path in your config is correct
2. Try restarting the MCP client
3. Check logs in stderr

## What Changed

| Issue | Before | After |
|-------|--------|-------|
| **SDK** | FastMCP | Official MCP SDK |
| **Transport** | Custom | Standard stdio |
| **Unicode** | Errors on Windows | Fixed ✅ |
| **Compare Loop** | Recursive calls | Fixed ✅ |
| **Compatibility** | Limited | All MCP clients ✅ |

## Need More Info?

- Full docs: `README_PYTHON_MCP.md`
- Technical details: `FIXES_APPLIED.md`
- Examples: `test_client.py`
