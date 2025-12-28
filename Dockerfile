# Dockerfile for Manim MCP Server
# This Dockerfile includes all system dependencies required for Manim on Linux

FROM python:3.11-slim

# Install system dependencies required for compiling pycairo and running Manim
# These are needed because Linux doesn't have pre-built wheels like Windows does
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mcp_server.py .
COPY mcpconfig.json .

# Expose port for FastAPI
EXPOSE 8000

# Run the MCP server
CMD ["python", "mcp_server.py"]
