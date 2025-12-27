#!/bin/bash

# Manim Animation Generator - Startup Script
# Starts both MCP Server and Streamlit App

echo ""
echo "========================================"
echo "  Manim Animation Generator"
echo "  Starting Services..."
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements-mcp.txt
    pip install -r requirements-streamlit.txt
fi

# Start MCP Server in background
echo ""
echo "Starting MCP Server on http://localhost:8000..."
python mcp_server.py &
MCP_PID=$!
sleep 3

# Start Streamlit App in new terminal (macOS) or same terminal (Linux)
echo "Starting Streamlit App on http://localhost:8501..."
streamlit run streamlit_app.py

# Cleanup
trap "kill $MCP_PID" EXIT
