# 🚀 Quick Start Guide - Airbnb MCP Server (Python)

## Installation (2 minutes)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test the Server
```bash
# Run the test client
python test_client.py
```

### Step 3: Start MCP Server
```bash
# Run the server
python server.py
```

## Configuration for AI Assistants

### For Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "python",
      "args": [
        "/absolute/path/to/server.py"
      ]
    }
  }
}
```

### For Cursor
1. Go to Settings > Tools & Integrations > MCP Servers
2. Add new server:
```json
{
  "airbnb": {
    "command": "python",
    "args": [
      "C:\\path\\to\\server.py"
    ]
  }
}
```

## 🎯 Example Usage

Once configured, you can ask your AI assistant:

### Search Examples
- "Search for Airbnb listings in Paris for 2 adults from Nov 1-5"
- "Find pet-friendly listings in Austin under $200/night"
- "Show me beachfront properties in Miami for next weekend"

### Details Examples
- "Get details for listing ID 12345678"
- "Show me the amenities and house rules for this property"
- "What are the reviews saying about listing 87654321?"

### Comparison Examples
- "Compare these 3 listings: 12345678, 87654321, 11223344"
- "Which of these properties has better reviews?"
- "Show me a side-by-side comparison with pricing"

### Price Calculator Examples
- "Calculate the total cost for listing 12345678 from Nov 1-5 for 2 adults"
- "What's the price breakdown including all fees?"
- "How much will it cost for a week stay?"

## 🔧 Customization

### Adjust Cache Duration
Edit `server.py`:
```python
CACHE_TTL = 600  # 10 minutes instead of 5
```

### Change Request Timeout
```python
REQUEST_TIMEOUT = 60.0  # 60 seconds instead of 30
```

### Enable Debug Logging
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Tips

1. **Use Cache**: Repeated searches are instant (5-min cache)
2. **Batch Comparisons**: Compare multiple listings in one call
3. **Clear Cache**: Use `clear_cache` tool when needed

## ❓ Troubleshooting

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Connection Timeout
- Check internet connection
- Increase `REQUEST_TIMEOUT`
- Verify Airbnb is accessible

### Page Structure Error
- Airbnb updated their HTML
- Check the `#data-deferred-state-0` script tag
- Update extraction logic if needed

### Cache Issues
- Call `clear_cache` tool
- Restart the server
- Reduce `CACHE_TTL`

## 🆚 Python vs TypeScript

| Feature | TypeScript | Python |
|---------|-----------|--------|
| Setup Time | ~5 min | ~2 min |
| Dependencies | npm, node | pip only |
| Performance | Good | Better (async) |
| Caching | ❌ | ✅ |
| Extra Tools | 2 | 5 |
| Type Safety | ✅ | ✅ |

## 🎓 Learning Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [httpx Async Guide](https://www.python-httpx.org/)
- [BeautifulSoup4 Docs](https://www.crummy.com/software/BeautifulSoup/)

## 🚀 Next Steps

1. Try the example queries above
2. Explore the comparison tool with real listings
3. Use the price calculator for trip planning
4. Check out the caching for faster responses
5. Contribute new features!

## 💡 Pro Tips

- Use specific dates for better pricing
- Cache persists for 5 minutes - great for comparisons
- Compare tool handles up to 5 listings
- Price calculator estimates - actual prices may vary
- Images array contains direct URLs to property photos

---

**Happy Searching! 🏠✨**
