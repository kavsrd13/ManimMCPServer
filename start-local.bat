@echo off
REM Manim Animation Generator - Startup Script
REM Starts both MCP Server and Streamlit App in separate windows

echo.
echo ========================================
echo  Manim Animation Generator
echo  Starting Services...
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Error: Virtual environment not found.
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements-mcp.txt
    pip install -r requirements-streamlit.txt
)

REM Start MCP Server
echo.
echo Starting MCP Server on http://localhost:8000...
start cmd /k "python mcp_server.py"
timeout /t 3

REM Start Streamlit App
echo Starting Streamlit App on http://localhost:8501...
start cmd /k "streamlit run streamlit_app.py"

echo.
echo ========================================
echo  Services Started!
echo  
echo  MCP Server: http://localhost:8000
echo  Streamlit App: http://localhost:8501
echo ========================================
echo.

pause
