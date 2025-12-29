# Streamlit Cloud Deployment Guide

## ✅ Code Successfully Pushed to GitHub

**Repository**: https://github.com/kavsrd13/ManimMCPServer
**Branch**: main
**Commit**: Production update with two-step AI enhancement

---

## 🚀 Deploy on Streamlit Cloud

### Step 1: Go to Streamlit Cloud
Visit: https://share.streamlit.io/

### Step 2: Create New App
1. Click **"New app"**
2. Select your repository: `kavsrd13/ManimMCPServer`
3. Set branch: `main`
4. Set main file path: `streamlit_app.py`
5. Click **"Deploy"**

### Step 3: Configure Environment Variables
In Streamlit Cloud settings, add these secrets:

```toml
# .streamlit/secrets.toml format

AZURE_OPENAI_API_KEY = "your-azure-openai-api-key-here"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4"
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
```

**How to add secrets:**
1. Go to your app dashboard
2. Click **"⋮"** (three dots) → **"Settings"**
3. Navigate to **"Secrets"** section
4. Paste the above configuration with your actual values
5. Click **"Save"**

---

## 🌐 Your App Will Be Live At:
`https://your-app-name.streamlit.app`

The app will automatically:
- ✅ Detect it's in production (not local)
- ✅ Connect to Azure Container Apps: https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io
- ✅ Use two-step AI enhancement
- ✅ Handle LaTeX-free rendering
- ✅ Show 3-step progress (enhance → generate → render)

---

## 📋 What's Deployed

### Production Files (on GitHub):
- ✅ `streamlit_app.py` - Main Streamlit app
- ✅ `mcp_server.py` - FastAPI server (already on Azure)
- ✅ `requirements.txt` - Python dependencies
- ✅ `requirements-backend.txt` - Backend dependencies
- ✅ `Dockerfile` - Container configuration
- ✅ `.gitignore` - Excludes local dev files

### Local Files (NOT on GitHub):
- ❌ `local_server.py` - Local development only
- ❌ `streamlit_app_local.py` - Local development only
- ❌ `test_local_server.py` - Testing only
- ❌ Deployment scripts (PowerShell)
- ❌ Documentation files
- ❌ Virtual environment

---

## 🧪 Test Your Deployment

Once deployed on Streamlit Cloud, test with these prompts:

1. **Simple animation**:
   ```
   Create a blue circle that transforms into a red square
   ```

2. **Math animation**:
   ```
   Show the Pythagorean theorem: a² + b² = c² with a visual proof
   ```

3. **Complex animation**:
   ```
   Explain gradient descent: show a ball rolling down a curve to find the minimum
   ```

---

## 🔍 Troubleshooting

### If app shows "Credentials incomplete":
- Check that all 4 environment variables are set in Streamlit secrets
- Verify no extra spaces in the values

### If generation fails:
- Check Azure OpenAI quota/limits
- Verify deployment name matches your Azure resource
- Test the backend server: https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io/status

### If timeout errors:
- Try a simpler prompt
- Complex animations may take up to 5 minutes

---

## 📊 Architecture

```
┌──────────────────────────────────┐
│   Streamlit Cloud (Public)       │
│   https://your-app.streamlit.app │
│                                  │
│   • streamlit_app.py             │
│   • Azure OpenAI integration     │
│   • Two-step enhancement         │
└────────────┬─────────────────────┘
             │ HTTPS POST
             │ /generate_animation
             ↓
┌──────────────────────────────────┐
│   Azure Container Apps           │
│   manim-mcp-app                  │
│                                  │
│   • mcp_server.py (FastAPI)      │
│   • Manim rendering engine       │
│   • LaTeX sanitization           │
│   • 5-minute timeout             │
└──────────────────────────────────┘
```

---

## ✨ Key Features

### User Experience
- 🎨 Natural language input
- 🔍 AI prompt enhancement (shows enhanced version)
- 🤖 Smart code generation (LaTeX-free)
- 🎬 Cloud rendering with progress tracking
- 📥 Download MP4 videos

### Technical
- ⚡ Two-step AI process for better results
- 🛡️ Robust error handling with debugging info
- 🚀 Scalable cloud infrastructure
- 📊 Progress indicators for 3 steps
- 🔧 Automatic LaTeX-to-Unicode conversion

---

## 🎉 Next Steps

1. ✅ Deploy on Streamlit Cloud
2. ✅ Add environment variables
3. ✅ Test with sample prompts
4. ✅ Share your app URL!

Your production app is ready to create stunning mathematical animations! 🎬
