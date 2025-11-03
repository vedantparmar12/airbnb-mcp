"""
Vercel Serverless Function for Backend API
"""
import sys
import os

# Add parent directory to path to import backend_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_server import app

# Vercel expects a handler
handler = app
