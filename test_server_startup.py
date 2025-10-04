#!/usr/bin/env python3
"""
Quick test to check if the server starts without unicode errors
"""

import subprocess
import sys
import time

def test_startup():
    """Test if server starts without unicode errors"""
    print("Testing server startup...")
    
    # Start the server process
    try:
        proc = subprocess.Popen(
            [sys.executable, "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Wait a bit for startup
        time.sleep(2)
        
        # Check if process is still running
        if proc.poll() is None:
            print("[OK] Server started successfully!")
            proc.terminate()
            proc.wait(timeout=5)
            return True
        else:
            stdout, stderr = proc.communicate()
            print("[FAIL] Server exited unexpectedly")
            print(f"STDOUT:\n{stdout}")
            print(f"STDERR:\n{stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error during startup test: {e}")
        return False

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1)
