# 🔍 Local vs Cloud Comparison

## File Comparison

### local_server.py (FastMCP Server)
✅ **Protocol:** FastMCP (Model Context Protocol)  
✅ **Port:** 8001  
✅ **Tools:** `generate_animation`, `validate_manim_code`, `get_server_status`  
✅ **Best for:** Local development with MCP protocol  

### mcp_server.py (Azure - FastAPI)
✅ **Protocol:** FastAPI (REST API)  
✅ **Port:** 8000  
✅ **Endpoints:** `/generate_animation`, `/validate_manim_code`, `/status`  
✅ **Best for:** Azure Container Apps deployment  

---

### streamlit_app_local.py (THIS FILE - For Local Testing)
✅ **Always connects to:** `http://localhost:8001` (FastMCP)  
✅ **Protocol:** JSON-RPC (MCP)  
✅ **Page title:** "LOCAL - Visualize Your Imagination"  
✅ **Shows banner:** "LOCAL DEVELOPMENT MODE"  
✅ **Error messages:** Guides you to start local FastMCP server  
✅ **Best for:** Testing animations locally with FastMCP  

### streamlit_app.py (Cloud Deployment)
✅ **Auto-detects environment:**
   - Local: Uses `http://localhost:8001`
   - Cloud: Uses Azure Container Apps  
✅ **Protocol:** REST API (FastAPI)  
✅ **Page title:** "See your Imagination come to Life"  
✅ **No banner:** Clean production look  
✅ **Error messages:** Generic connection errors  
✅ **Best for:** Deployed on Streamlit Cloud  

---

## How to Test

### Test Local Version:
1. Start local server: `python local_server.py`
2. Run: `streamlit run streamlit_app_local.py`
3. Should show: "LOCAL DEVELOPMENT MODE" at the top
4. Sidebar shows: "Environment: Local Development"

### Test Cloud Version Locally:
1. Start local server: `python local_server.py`
2. Run: `streamlit run streamlit_app.py`
3. Should show: Regular title (no LOCAL banner)
4. Sidebar shows: "Environment: Local (Development)"

### Test Cloud Version on Streamlit Cloud:
1. Deploy `streamlit_app.py` to Streamlit Cloud
2. Should automatically use Azure Container Apps URL
3. Sidebar shows: "Environment: Azure (Production)"

---

## Quick Start Commands

**Start everything for local development:**
```bash
run_local.bat
```

**Or start manually:**
```bash
# Terminal 1: Start local server
python local_server.py

# Terminal 2: Start local Streamlit app
streamlit run streamlit_app_local.py
```

---

## Visual Differences When Running

### Local App (streamlit_app_local.py)
```
🎬 Visualize Your Imagination
🖥️ LOCAL DEVELOPMENT MODE
ℹ️ This version connects to your local FastMCP server at http://localhost:8001

Sidebar shows:
- Local FastMCP Server: ✅ Running
- Protocol: FastMCP (MCP)
- Environment: Local Development

[Rest of the app...]
```

### Cloud App (streamlit_app.py)
```
🎬 Visualize Your Imagination
Create stunning animations from your ideas!

[Rest of the app...]
```

---

## Which One Should I Run?

| Scenario | Use This File |
|----------|--------------|
| Testing locally | `streamlit_app_local.py` |
| Deployed to Streamlit Cloud | `streamlit_app.py` |
| Want to see local vs cloud difference | Run both! |
