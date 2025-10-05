#!/usr/bin/env python3
"""
Direct test of Airbnb search to see raw data structure
"""

import sys
import io
import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote, urlencode

# Fix Windows encoding
if sys.platform == 'win32':
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "https://www.airbnb.com"
USER_AGENT = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"

async def fetch_airbnb_raw(location: str, checkin: str, checkout: str, adults: int):
    """Fetch raw Airbnb data to inspect structure"""

    # Build URL
    search_url = f"{BASE_URL}/s/{quote(location)}/homes?"
    params = {
        "checkin": checkin,
        "checkout": checkout,
        "adults": str(adults)
    }
    full_url = search_url + urlencode(params)

    print(f"Fetching: {full_url}\n")

    # Fetch HTML
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cache-Control": "no-cache",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(full_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            html = await response.text()

    print(f"Got HTML response: {len(html)} chars\n")

    # Parse
    soup = BeautifulSoup(html, 'html.parser')
    script_elem = soup.find('script', {'id': 'data-deferred-state-0'})

    if not script_elem:
        print("ERROR: Could not find #data-deferred-state-0")
        return

    print("Found data script element\n")

    # Parse JSON
    data = json.loads(script_elem.string)

    if 'niobeClientData' not in data:
        print(f"ERROR: No niobeClientData. Keys: {list(data.keys())}")
        return

    client_data = data['niobeClientData'][0][1]
    results = client_data['data']['presentation']['staysSearch']['results']

    search_results = results.get('searchResults', [])

    print(f"✓ Found {len(search_results)} search results\n")

    if len(search_results) > 0:
        print("=" * 80)
        print("FIRST RESULT STRUCTURE:")
        print("=" * 80)

        first = search_results[0]

        print(f"\nTop-level keys: {list(first.keys())}\n")

        # Check for listing
        if 'listing' in first:
            print(f"✓ Has 'listing' field")
            print(f"  Listing keys: {list(first['listing'].keys())}\n")

            if 'id' in first['listing']:
                print(f"  ✓ Has 'id': {first['listing']['id'][:50]}...")
            else:
                print(f"  ✗ No 'id' in listing")
        else:
            print("✗ No 'listing' field\n")

        # Check for other common fields
        if 'structuredDisplayPrice' in first:
            print(f"✓ Has 'structuredDisplayPrice'")

        if 'structuredContent' in first:
            print(f"✓ Has 'structuredContent'")

        # Print full first result (truncated)
        print("\n" + "=" * 80)
        print("FULL FIRST RESULT (first 2000 chars):")
        print("=" * 80)
        print(json.dumps(first, indent=2)[:2000])
        print("\n... (truncated)")

        # Save full results to file
        with open("airbnb_raw_results.json", "w", encoding="utf-8") as f:
            json.dump(search_results[:3], f, indent=2)

        print(f"\n✓ Saved first 3 results to airbnb_raw_results.json")
    else:
        print("No search results found!")

async def main():
    await fetch_airbnb_raw(
        location="Goa, India",
        checkin="2025-10-05",
        checkout="2025-10-07",
        adults=2
    )

if __name__ == "__main__":
    asyncio.run(main())
