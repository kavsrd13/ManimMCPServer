# FastMCP Cloud Deployment Checklist

## Pre-Deployment Checklist

- [ ] FastMCP Cloud account created at https://cloud.fastmcp.io
- [ ] FastMCP CLI installed: `pip install fastmcp`
- [ ] Logged in to FastMCP: `fastmcp login`
- [ ] Git repository initialized (if using GitHub integration)
- [ ] All files committed and pushed to GitHub (if needed)

## Deployment Steps

### Step 1: Prepare for Deployment
```bash
# Verify all necessary files exist
ls mcpconfig.json Dockerfile requirements-mcp.txt mcp_server.py
```

### Step 2: Deploy to FastMCP Cloud

**Option A: Using FastMCP CLI (Recommended)**
```bash
# Login to FastMCP
fastmcp login

# Deploy
fastmcp deploy

# Get deployment URL
fastmcp status
```

**Option B: Using Docker**
```bash
# Build Docker image
docker build -t manim-mcp-server .

# Test locally
docker run -p 8000:8000 manim-mcp-server

# Push to registry and deploy via dashboard
```

### Step 3: Retrieve Deployment URL
After successful deployment, you'll get a URL like:
```
https://manim-mcp-server-xxxxx.fastmcp.io
```

### Step 4: Update Streamlit Configuration

**Option A: Update .env for local Streamlit testing**
```bash
# Edit .env
MCP_SERVER_URL=https://manim-mcp-server-xxxxx.fastmcp.io
```

**Option B: Update Streamlit Cloud settings**
1. Go to Streamlit Cloud Dashboard
2. Select your app
3. Click Settings → Secrets
4. Add: `MCP_SERVER_URL = https://manim-mcp-server-xxxxx.fastmcp.io`

### Step 5: Test Deployment

```bash
# Test the deployed server
curl https://manim-mcp-server-xxxxx.fastmcp.io/status

# Expected output:
# {
#   "status": "running",
#   "server_name": "Manim Animation Server",
#   ...
# }
```

### Step 6: Monitor and Configure

1. **Access FastMCP Cloud Dashboard**
2. **Configure:**
   - Resource allocation (memory, CPU)
   - Timeout settings (recommended: 300-600s)
   - Environment variables
   - Auto-scaling rules

3. **Monitor:**
   - View logs
   - Track resource usage
   - Set up alerts

## Post-Deployment Verification

- [ ] `/status` endpoint returns running status
- [ ] `/` endpoint shows API information
- [ ] Test animation generation with sample Manim code
- [ ] Streamlit app successfully connects to FastMCP Cloud server
- [ ] Videos are generated and returned correctly

## Rollback Plan

If deployment has issues:

1. Keep local server running as backup
2. Revert `MCP_SERVER_URL` to `http://localhost:8000`
3. Check logs in FastMCP Cloud dashboard
4. Fix issues and redeploy

## Support & Troubleshooting

- **FastMCP Cloud Issues**: https://docs.fastmcp.io
- **Manim Issues**: https://docs.manim.community/
- **Local Testing**: Run `python mcp_server.py` locally

## Important URLs

- FastMCP Cloud Dashboard: https://cloud.fastmcp.io
- Your Deployed Server: https://manim-mcp-server-xxxxx.fastmcp.io
- Streamlit App: [Your Streamlit Cloud URL]
- Local Testing: http://localhost:8000

---

**After successful deployment, your Manim Animation Generator is ready for production use!**
