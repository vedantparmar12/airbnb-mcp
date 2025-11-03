"""
Configuration module for Airbnb MCP Server
"""

import sys

# Airbnb Settings
BASE_URL = "https://www.airbnb.com"
USER_AGENT = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"
REQUEST_TIMEOUT = 30

# MCP Settings
IGNORE_ROBOTS_TXT = "--ignore-robots-txt" in sys.argv

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
