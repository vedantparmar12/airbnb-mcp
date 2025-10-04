#!/usr/bin/env python3
"""
Test the extraction logic to debug Airbnb scraping
"""

import asyncio
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

async def test_extraction():
    """Test extracting data from a simple Airbnb search"""
    from server import airbnb_search
    
    print("Testing Airbnb extraction...")
    print("=" * 60)
    
    try:
        result = await airbnb_search(location="Paris, France", limit=3)
        print("\nResult:")
        print(result)
        return True
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_extraction())
    sys.exit(0 if success else 1)
