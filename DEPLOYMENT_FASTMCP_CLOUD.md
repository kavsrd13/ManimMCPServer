# 🚀 FastMCP Cloud Deployment Guide (Updated)

This guide provides the correct methods to deploy your Manim Animation MCP Server to FastMCP Cloud.

## Available Deployment Methods

### Method 1: Using FastMCP CLI (Direct Deployment)

1. **Test locally first:**
```bash
fastmcp dev
```

2. **For production deployment:**
```bash
# Deploy to FastMCP Cloud
fastmcp deploy --name manim-animation-server
```

Or deploy through the FastMCP Cloud dashboard for more control.

### Method 2: Docker Container Deployment (Recommended)

1. **Build Docker image:**
```bash
docker build -t manim-mcp-server:latest .
```

2. **Test locally:**
```bash
docker run -p 8000:8000 manim-mcp-server:latest
```

3. **Deploy to FastMCP Cloud via Dashboard:**
   - Go to [FastMCP Cloud Dashboard](https://cloud.fastmcp.io)
   - Click "Create New Deployment"
   - Select "Docker"
   - Upload or push your Docker image
   - Configure resources and environment variables
   - Deploy

### Method 3: GitHub Integration (Easiest)

1. **Initialize Git repository:**
```bash
git init
git add .
git commit -m "Initial commit: Manim Animation MCP Server"
git remote add origin https://github.com/YOUR_USERNAME/manim-mcp-server.git
git push -u origin main
```

2. **Connect to FastMCP Cloud:**
   - Go to [FastMCP Cloud Dashboard](https://cloud.fastmcp.io)
   - Click "Settings"
   - Connect GitHub account
   - Select your repository
   - Enable auto-deployment
   - Configure branch (main)

3. **Auto-Deployment:**
   - Every push to main will automatically redeploy your server
   - Check deployment status in dashboard

## FastMCP CLI Commands

```bash
# Check version
fastmcp version

# Run server locally for testing
fastmcp dev

# Run in production mode
fastmcp run

# Inspect MCP server tools
fastmcp inspect

# Project management
fastmcp project list
fastmcp project create
fastmcp project delete

# Install tools/packages
fastmcp install <package>

# Task management
fastmcp tasks list
fastmcp tasks run <task>
```

## Environment Variables for Cloud Deployment

Set these in FastMCP Cloud Dashboard:

```env
# Optional customization
MANIM_QUALITY=low_quality    # Options: low_quality, medium_quality, high_quality
EXECUTION_TIMEOUT=300        # Seconds (default: 180)
PYTHONUNBUFFERED=1          # Keep Python output unbuffered
```

## Configuration Files

### mcpconfig.json
Defines how FastMCP Cloud runs your server:
```json
{
  "mcpServers": {
    "manim-animation-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Dockerfile
Container configuration with all dependencies:
```dockerfile
FROM python:3.10-slim

# Install FFmpeg and LaTeX
RUN apt-get update && apt-get install -y ffmpeg texlive texlive-latex-extra ...

# Setup and run server
WORKDIR /app
COPY requirements-mcp.txt .
RUN pip install -r requirements-mcp.txt
COPY mcp_server.py .

EXPOSE 8000
CMD ["python", "mcp_server.py"]
```

## Testing Your Deployment

After deployment, test these endpoints:

```bash
# Get server status
curl https://your-deployment.fastmcp.io/status

# Validate Manim code
curl -X POST https://your-deployment.fastmcp.io/validate_manim_code \
  -H "Content-Type: application/json" \
  -d '{"manim_code": "from manim import *\n\nclass GeneratedScene(Scene):\n    def construct(self):\n        circle = Circle()\n        self.play(Create(circle))"}'

# Generate animation
curl -X POST https://your-deployment.fastmcp.io/generate_animation \
  -H "Content-Type: application/json" \
  -d '{"manim_code": "..."}'
```

## Scaling Configuration

FastMCP Cloud automatically handles scaling, but you can configure:

1. **Memory allocation:** 2-4GB (recommended for Manim)
2. **CPU cores:** 2+ (recommended for video rendering)
3. **Concurrency:** Handle multiple requests in parallel
4. **Timeout:** Set to 300-600 seconds (Manim rendering takes time)

## Cost Optimization

- Use low quality mode (`-ql`) for faster, cheaper rendering
- Set appropriate timeout values to avoid hanging processes
- Monitor concurrent requests to optimize resources
- Use caching for repeated animations (future enhancement)

## Troubleshooting

### Command Not Found: fastmcp
```bash
pip install fastmcp --upgrade
```

### Docker Build Fails
- Ensure Docker is installed: `docker --version`
- Check Dockerfile syntax
- Verify all files exist in directory

### Deployment Fails
- Check FastMCP Cloud dashboard logs
- Verify `mcpconfig.json` is valid JSON
- Ensure Python dependencies are all in `requirements-mcp.txt`
- Check that FFmpeg is properly installed in Docker

### Server Timeout
- Increase timeout in environment variables
- Use lower quality Manim output
- Check logs for hanging processes

### Authentication Issues
- Verify GitHub token is valid (if using GitHub integration)
- Check FastMCP Cloud credentials
- Try deploying via dashboard instead of CLI

## Resource Requirements

For optimal Manim rendering:
- **Memory:** 2-4GB
- **CPU:** 2 cores minimum
- **Storage:** 10GB (for temporary animation files)
- **Timeout:** 300-600 seconds

## Support

- **FastMCP Docs:** https://docs.fastmcp.io
- **Manim Docs:** https://docs.manim.community/
- **FastMCP GitHub:** https://github.com/jlowin/fastmcp
- **Issues:** Check FastMCP GitHub issues for known problems

## Next Steps

1. Choose your deployment method (Docker + GitHub is recommended)
2. Test locally with `fastmcp dev`
3. Deploy to FastMCP Cloud
4. Update Streamlit app with new server URL
5. Monitor deployment in FastMCP Cloud dashboard

---

**Your MCP server is now ready for cloud deployment!**
