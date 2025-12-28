# FastMCP Build Error Troubleshooting Guide

## Issues Found and Fixed

### 1. ❌ Missing Python Imports in mcp_server.py
**Problem:** The code referenced undefined classes and modules
- Missing `from typing import Optional`
- Missing `from fastapi import HTTPException`
- Missing `from pydantic import BaseModel`
- Missing `import uvicorn`
- Missing `app` variable definition
- Missing `ManimCodeRequest` class

**Status:** ✅ FIXED - All imports and classes added to mcp_server.py

---

### 2. ❌ Problematic Dependency: pycairo==1.26.0
**Problem:** `pycairo` requires system-level Cairo graphics library that's not available in standard Docker containers

**Error Message:**
```
ERROR: failed to solve: process "/bin/sh -c if [ -n \"$DETECTED_REQUIREMENTS\" ]...
exit code: 1
```

**Status:** ✅ FIXED - Commented out pycairo in requirements files

---

### 3. ❌ Manim System Dependencies Not Available
**Problem:** Manim requires system packages that aren't included in FastMCP's base image:
- `ffmpeg` - for video encoding
- `libcairo2-dev` - Cairo graphics library
- `libpango1.0-dev` - text rendering
- `texlive` - LaTeX support for mathematical notation

**Impact:** Even if Python packages install, Manim won't work without these system packages

---

## Solutions & Next Steps

### Option 1: Use Custom Dockerfile (RECOMMENDED if FastMCP supports it)

1. **Check if FastMCP supports custom Dockerfiles:**
   - Look in FastMCP dashboard for "Custom Docker" or "Dockerfile" option
   - Some platforms auto-detect Dockerfile in repository

2. **If supported:**
   - Push the `Dockerfile` to your repository
   - Redeploy on FastMCP
   - The Dockerfile installs all system dependencies

### Option 2: Contact FastMCP Support

**Ask them:**
1. Does FastMCP support custom Dockerfiles?
2. Can they add system packages to their base image:
   - ffmpeg
   - libcairo2-dev
   - pkg-config
   - libpango1.0-dev
   - texlive-latex-extra

3. Is there a way to specify apt packages in a config file?

### Option 3: Minimal Deployment (Testing Only)

If you just want to verify the MCP server infrastructure works:

1. **Rename requirements files:**
   ```bash
   mv requirements.txt requirements-full.txt
   mv requirements-minimal.txt requirements.txt
   ```

2. **Modify mcp_server.py to skip Manim execution:**
   - Comment out actual Manim execution
   - Return mock video data for testing

3. **Deploy to FastMCP**

4. **Verify MCP tools are callable**

### Option 4: Alternative Cloud Platform

Consider deploying to a platform that supports custom Dockerfiles:
- **Railway** - Supports Dockerfile, generous free tier
- **Render** - Free tier with Docker support
- **Google Cloud Run** - Pay-as-you-go with Docker support
- **Fly.io** - Free tier with Dockerfile support
- **AWS App Runner** or **Azure Container Apps**

---

## Testing the Fixed Code Locally

Before redeploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure system packages are installed (Linux/Mac):
# Ubuntu/Debian:
sudo apt-get install ffmpeg libcairo2-dev pkg-config libpango1.0-dev texlive-latex-extra

# macOS (Homebrew):
brew install cairo pango ffmpeg
brew install --cask mactex-no-gui

# Run the server
python mcp_server.py
```

The server should start without errors on http://localhost:8000

---

## Quick Reference: What Was Fixed

### mcp_server.py
- ✅ Added missing imports: `Optional`, `HTTPException`, `BaseModel`, `uvicorn`
- ✅ Created `app` variable from `mcp.app`
- ✅ Created `ManimCodeRequest` class

### requirements.txt & requirements-mcp.txt
- ✅ Commented out `pycairo==1.26.0`
- ✅ Added notes about system dependencies

### New Files
- ✅ `Dockerfile` - Complete Docker setup with system dependencies
- ✅ `.dockerignore` - Optimized Docker builds
- ✅ `requirements-minimal.txt` - Testing without Manim
- ✅ `FASTMCP_TROUBLESHOOTING.md` - This guide

---

## Expected Behavior After Fix

### If using Dockerfile:
- ✅ Build should complete successfully
- ✅ All system dependencies installed
- ✅ Manim animations will work

### If using standard FastMCP (without Dockerfile):
- ⚠️ Build will succeed if using requirements-minimal.txt
- ❌ Manim won't work (missing system packages)
- ✅ MCP tools will be callable but return errors when trying to render

---

## Recommended Action Plan

1. **Commit all fixes:**
   ```bash
   git add .
   git commit -m "Fix: Add missing imports and handle system dependencies"
   git push origin main
   ```

2. **Check FastMCP documentation:**
   - Look for Dockerfile support
   - Check for system package configuration options

3. **Try deployment with Dockerfile first**

4. **If Dockerfile not supported:**
   - Use requirements-minimal.txt
   - Contact FastMCP support about adding system packages
   - OR migrate to alternative platform that supports Docker

5. **Monitor build logs** for specific error messages

---

## Contact & Support

If you continue having issues:

1. **Share the exact build log** from FastMCP
2. **Check FastMCP documentation** for custom runtime support
3. **Ask in FastMCP Discord/Forum** about Manim deployment
4. **Consider alternatives** if FastMCP doesn't support required dependencies

---

Good luck! The code issues are now fixed. The remaining challenge is ensuring the deployment platform has the necessary system libraries for Manim.
