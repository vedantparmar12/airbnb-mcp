#!/usr/bin/env python3
"""
Correct test client for the Airbnb MCP Server.

This client starts the server as a subprocess and communicates with it
over stdin/stdout using the JSON-based Model Context Protocol.
"""

import asyncio
import json
import sys


async def run_test():
    """Starts the server and runs a series of tool calls."""

    print("Starting server subprocess...")
    process = await asyncio.create_subprocess_exec(
        sys.executable, "server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def send_request(request: dict):
        request_json = json.dumps(request)
        print(f"--> SENDING: {request_json}")
        process.stdin.write(request_json.encode() + b'\n')
        await process.stdin.drain()

    async def read_response():
        response_json = await process.stdout.readline()
        if not response_json:
            return None
        response = json.loads(response_json)
        print(f"<-- RECEIVED: {json.dumps(response, indent=2)}")
        return response

    try:
        # 1. Initialize
        print("\n" + "="*60)
        print("TEST 1: Initialize")
        print("="*60)
        await send_request({"type": "initialize", "id": "test-1"})
        init_response = await read_response()
        assert init_response['type'] == 'initialize/response'

        # 2. Search for a listing
        print("\n" + "="*60)
        print("TEST 2: airbnb_search")
        print("="*60)
        search_request = {
            "type": "tools/call",
            "id": "test-2",
            "tool_name": "airbnb_search",
            "parameters": {"location": "Paris, France", "limit": 5}
        }
        await send_request(search_request)
        search_response = await read_response()
        assert search_response['type'] == 'tools/response'
        assert search_response['id'] == 'test-2'
        
        search_output = json.loads(search_response['output'])
        assert isinstance(search_output, list)
        listing_id = search_output[0]['id']
        print(f"SUCCESS: Found listing ID: {listing_id}")

        # 3. Get listing details
        print("\n" + "="*60)
        print(f"TEST 3: airbnb_listing_details (id: {listing_id})")
        print("="*60)
        details_request = {
            "type": "tools/call",
            "id": "test-3",
            "tool_name": "airbnb_listing_details",
            "parameters": {"id": listing_id}
        }
        await send_request(details_request)
        details_response = await read_response()
        assert details_response['type'] == 'tools/response'
        details_output = json.loads(details_response['output'])
        assert details_output['id'] == listing_id
        print("SUCCESS: Fetched details.")

        # 4. Compare listings
        print("\n" + "="*60)
        print("TEST 4: airbnb_compare_listings")
        print("="*60)
        compare_request = {
            "type": "tools/call",
            "id": "test-4",
            "tool_name": "airbnb_compare_listings",
            "parameters": {"ids": [listing_id, search_output[1]['id']]}
        }
        await send_request(compare_request)
        compare_response = await read_response()
        assert compare_response['type'] == 'tools/response'
        compare_output = json.loads(compare_response['output'])
        assert len(compare_output) == 2
        print("SUCCESS: Compared listings.")

        # 5. Clear cache
        print("\n" + "="*60)
        print("TEST 5: clear_cache")
        print("="*60)
        clear_cache_request = {
            "type": "tools/call",
            "id": "test-5",
            "tool_name": "clear_cache",
            "parameters": {}
        }
        await send_request(clear_cache_request)
        clear_cache_response = await read_response()
        assert clear_cache_response['type'] == 'tools/response'
        assert "success" in clear_cache_response['output'].lower()
        print("SUCCESS: Cleared cache.")

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        # Print any remaining stderr from the server
        stderr = await process.stderr.read()
        if stderr:
            print("\n--- Server Stderr ---")
            print(stderr.decode())
            print("---------------------")

    finally:
        print("\nTerminating server process...")
        process.terminate()
        await process.wait()
        print("Server terminated.")

if __name__ == "__main__":
    asyncio.run(run_test())
