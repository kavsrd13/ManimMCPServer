# 🚀 Deployment Options for Manim MCP Server

## ❌ FastMCP Cloud - **NOT COMPATIBLE**

### Why FastMCP Cloud Doesn't Work

FastMCP Cloud uses a **standard Python builder** that:
- ✅ Installs pure Python packages
- ❌ **Does NOT support custom Dockerfiles**
- ❌ **Does NOT include C compilers** (gcc, clang, cc)
- ❌ **Does NOT have system libraries** (Cairo, Pango, FFmpeg)

**Error Evidence:**
```
ERROR: Unknown compiler(s): [['cc'], ['gcc'], ['clang']...]
Running `cc --version` gave "[Errno 2] No such file or directory: 'cc'"
```

### Packages That Won't Work on FastMCP Cloud
- `pycairo` - Requires Cairo C libraries + compiler
- `manim` - Depends on pycairo, Cairo, Pango, FFmpeg, LaTeX
- Any package requiring system dependencies or compilation

---

## ✅ RECOMMENDED: Alternative Deployment Platforms

### Option 1: Railway (EASIEST)

**Why Railway:**
- ✅ Full Dockerfile support
- ✅ Free tier ($5/month credits)
- ✅ Auto-detects Dockerfile
- ✅ Easy deployment from GitHub
- ✅ Built-in domain + HTTPS

**Steps:**
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Dockerfile and builds
6. Get your deployment URL: `https://your-app.up.railway.app`

**Pricing:** Free $5/month credits, then ~$5-10/month

---

### Option 2: Render

**Why Render:**
- ✅ Full Dockerfile support
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ Custom domains

**Steps:**
1. Go to https://render.com
2. Sign up and connect GitHub
3. Create new "Web Service"
4. Select your repository
5. Render detects Dockerfile automatically
6. Deploy!

**Pricing:** Free tier (with sleep after inactivity), Paid from $7/month

---

### Option 3: Fly.io

**Why Fly.io:**
- ✅ Excellent Dockerfile support
- ✅ Free tier
- ✅ Fast global deployment
- ✅ Simple CLI tool

**Steps:**
1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Login: `flyctl auth login`
3. In your project directory:
   ```bash
   flyctl launch
   ```
4. Fly.io auto-detects Dockerfile
5. Deploy: `flyctl deploy`

**Pricing:** Free tier (3GB RAM, 160GB transfer), then pay-as-you-go

---

### Option 4: Google Cloud Run

**Why Cloud Run:**
- ✅ Full Docker support
- ✅ Pay-per-use (very cheap for low traffic)
- ✅ Auto-scaling
- ✅ Enterprise-grade

**Steps:**
1. Install gcloud CLI
2. Build container:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/manim-mcp
   ```
3. Deploy:
   ```bash
   gcloud run deploy manim-mcp \
     --image gcr.io/YOUR_PROJECT/manim-mcp \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

**Pricing:** Free tier (2M requests/month), then ~$0.40 per million requests

---

### Option 5: Azure Container Apps

**Why Azure:**
- ✅ Full Docker support
- ✅ Integrates with your Azure OpenAI
- ✅ Free tier
- ✅ Enterprise features

**Steps:**
1. Create Container Registry
2. Build and push Docker image
3. Create Container App
4. Deploy from registry

**Pricing:** Free tier available, then consumption-based

---

## 🔄 Option A: Minimal FastMCP Deployment (No Manim)

If you **must** use FastMCP Cloud, you can deploy a **minimal version**:

### What This Means:
- ✅ MCP server infrastructure works
- ✅ API endpoints accessible
- ❌ **Cannot actually render Manim animations**
- ✅ Can return mock/placeholder videos for testing

### Steps:

1. **Use minimal requirements:**
   ```bash
   mv requirements.txt requirements-full.txt
   cp requirements-minimal.txt requirements.txt
   ```

2. **Modify mcp_server.py to return mock data:**
   (See MOCK_IMPLEMENTATION.md for code)

3. **Deploy to FastMCP**
   - Push to GitHub
   - FastMCP will build successfully
   - Can test MCP infrastructure

4. **Limitation:**
   - No actual video generation
   - Only for testing the MCP protocol/infrastructure

---

## 📊 Platform Comparison

| Platform | Dockerfile | Free Tier | Ease | Best For |
|----------|-----------|-----------|------|----------|
| **Railway** | ✅ Yes | $5/mo credit | ⭐⭐⭐⭐⭐ | Quick deployment |
| **Render** | ✅ Yes | Yes (sleeps) | ⭐⭐⭐⭐ | Free hosting |
| **Fly.io** | ✅ Yes | Yes | ⭐⭐⭐⭐ | Global edge |
| **Cloud Run** | ✅ Yes | 2M req/mo | ⭐⭐⭐ | Production scale |
| **Azure** | ✅ Yes | Yes | ⭐⭐⭐ | Azure integration |
| **FastMCP** | ❌ **No** | Yes | ⭐⭐⭐⭐⭐ | **Simple Python only** |

---

## 🎯 Recommended Path Forward

### For Production (Real Manim Rendering):
1. **Choose Railway** (easiest) or **Render** (free tier)
2. Push your code with the existing Dockerfile
3. Platform auto-builds and deploys
4. Update Streamlit app with new URL
5. ✅ **Full Manim animations work!**

### For Testing (FastMCP Infrastructure):
1. Use `requirements-minimal.txt`
2. Mock the Manim execution
3. Deploy to FastMCP Cloud
4. Test MCP protocol integration
5. ⚠️ **No real animations, just testing**

---

## 🚀 Next Steps

**RECOMMENDED:** Deploy to Railway

```bash
# 1. Ensure Dockerfile is ready (already done!)
# 2. Push to GitHub (already done!)
# 3. Go to railway.app
# 4. Connect GitHub repo
# 5. Deploy automatically!
```

Your existing Dockerfile will work perfectly on any of these platforms!

---

## 💡 Key Takeaway

**FastMCP Cloud is designed for simple Python packages only.**

For anything requiring:
- System dependencies
- C compilation
- Custom Docker configurations

You need a platform that supports **custom Dockerfiles**.

Railway, Render, or Fly.io are your best options! 🎉
