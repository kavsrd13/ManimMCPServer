# 🎬 Manim Animation Generator

An intelligent animation generation system that converts natural language descriptions into mathematical animations using Manim. The system consists of a Streamlit web interface powered by Azure OpenAI and a FastMCP server for animation rendering.

## 🏗️ Architecture

```
Streamlit App (Cloud) 
    ↓ (Natural Language)
Azure OpenAI API (Converts to Manim Code)
    ↓ (Manim Code)
FastMCP Server (Renders Animation)
    ↓ (Video)
Streamlit App (Displays Result)
```

## 📋 Prerequisites

- Python 3.9 or higher
- Azure OpenAI API key and endpoint
- FastMCP Cloud account (for deployment)
- GitHub account (for code hosting)

## 🚀 Quick Start - Local Testing

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-mcp.txt
pip install -r requirements-streamlit.txt
```

### 2. Configure Environment

Create `.env` file:
```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
MCP_SERVER_URL=http://localhost:8000
```

### 3. Run Locally

**Terminal 1 - MCP Server:**
```bash
python mcp_server.py
```

**Terminal 2 - Streamlit App:**
```bash
streamlit run streamlit_app.py
```

## 🌐 Cloud Deployment

### Deploy to FastMCP Cloud

1. Push code to GitHub:
```bash
git push origin main
```

2. Go to FastMCP Cloud Dashboard: https://cloud.fastmcp.io

3. Create new deployment from GitHub repository

4. Get deployment URL (e.g., `https://manim-mcp-server.fastmcp.io`)

5. Update Streamlit Cloud secrets:
```
MCP_SERVER_URL = https://your-deployment-url.fastmcp.io
```

### Deploy Streamlit App to Streamlit Cloud

1. Push code to GitHub

2. Go to https://share.streamlit.io

3. Connect your repository

4. Add secrets in deployment settings:
```
AZURE_OPENAI_API_KEY = your_key
AZURE_OPENAI_ENDPOINT = your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME = your_deployment
MCP_SERVER_URL = https://your-mcp-server-url.fastmcp.io
```

The app will open in your browser at `http://localhost:8501`

## 🌐 Deployment
## 📁 Project Structure

```
MCPproject/
├── streamlit_app.py              # Streamlit UI
├── mcp_server.py                 # MCP Server with FastAPI
├── requirements-mcp.txt          # MCP Server dependencies
├── requirements-streamlit.txt    # Streamlit dependencies
├── mcpconfig.json                # FastMCP configuration
├── .streamlit/
│   └── config.toml              # Streamlit settings
├── .gitignore                    # Git ignore (protects .env)
├── .env                          # Local secrets (not in git)
└── README.md                     # This file
```

## 🔑 Key Features

- **Natural Language Input**: Describe animations in plain English
- **AI-Powered**: Uses Azure OpenAI to convert text to Manim code
- **Instant Rendering**: FastMCP server generates videos quickly
- **Web Interface**: Clean Streamlit UI for easy interaction
- **Cloud Ready**: Deploy on Streamlit Cloud + FastMCP Cloud

## 📝 Usage Example

1. Open Streamlit app
2. Enter: "Create a circle that morphs into a square"
3. Click "Generate Animation"
4. View and download the generated video

## 🔐 Security

- `.env` file is gitignored (secrets never pushed to GitHub)
- Use Streamlit Cloud secrets for production
- Use FastMCP Cloud secrets for MCP server

## 🛠️ Environment Variables

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY        # Your API key
AZURE_OPENAI_ENDPOINT       # Your endpoint URL
AZURE_OPENAI_DEPLOYMENT_NAME # Deployment name
AZURE_OPENAI_API_VERSION    # API version (2024-12-01-preview)

# MCP Server
MCP_SERVER_URL              # URL of FastMCP server
```

## 📚 Documentation

- **Manim**: https://docs.manim.community/
- **Streamlit**: https://docs.streamlit.io/
- **FastMCP**: https://docs.fastmcp.io/
- **Azure OpenAI**: https://learn.microsoft.com/en-us/azure/ai-services/openai/

## 🚀 Deployment Links

- Streamlit Cloud: https://share.streamlit.io
- FastMCP Cloud: https://cloud.fastmcp.io
- GitHub: https://github.com/kavsrd13/ManimMCPServer

## 📧 Support

For issues:
- Check error logs in respective dashboards
- Review Manim documentation for animation syntax
- Verify API credentials are correct

---

**Built with Azure OpenAI + FastMCP + Manim + Streamlit** 🎨
