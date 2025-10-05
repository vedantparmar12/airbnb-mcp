# LiveKit Agent Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy MCP server directory and its dependencies
COPY mcp-server-airbnb ./mcp-server-airbnb

# Install MCP server dependencies
WORKDIR /app/mcp-server-airbnb
RUN uv sync --frozen || pip install -r requirements.txt || true

# Back to main app directory
WORKDIR /app

# Copy main agent code
COPY livekit_mcp_agent.py .

# Note: .env is NOT copied - use LiveKit Cloud environment variables instead

# Run the agent
CMD ["uv", "run", "python", "livekit_mcp_agent.py", "start"]
