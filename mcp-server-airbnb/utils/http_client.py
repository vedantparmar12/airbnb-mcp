"""
HTTP client utilities for fetching Airbnb data
"""

import aiohttp
from config import USER_AGENT


async def fetch_with_user_agent(url: str, timeout: int = 30) -> str:
    """Fetch URL with proper headers"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cache-Control": "no-cache",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {response.reason}")
            return await response.text()
