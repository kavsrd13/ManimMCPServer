# 🎬 Manim Animation Generator

An intelligent animation generation system that converts natural language descriptions into mathematical animations using Manim. The system consists of a Streamlit web interface powered by Azure OpenAI and a FastMCP server for animation rendering.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│              (Streamlit App - Cloud Hosted)                 │
│                                                             │
│  1. User enters natural language description                │
│  2. Azure OpenAI converts to Manim code                     │
│  3. Sends code to MCP Server                                │
│  4. Receives & displays generated video                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ HTTP POST Request
                   │ (Manim Code)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Manim Server (FastMCP)                     │
│                                                             │
│  1. Receives Manim code via MCP tool                        │
│  2. Executes code in isolated environment                   │
│  3. Generates animation video (MP4)                         │
│  4. Returns base64-encoded video                            │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.9 or higher
- Azure OpenAI API access (API key and endpoint)
- FFmpeg installed (required by Manim)
- LaTeX distribution (optional, for complex mathematical formulas)

## 🚀 Setup Instructions

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd MCPproject

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

**For Streamlit App:**
```bash
pip install -r requirements-streamlit.txt
```

**For MCP Server:**
```bash
pip install -r requirements-mcp.txt
```

**Install FFmpeg:**
- Windows: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/)
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Azure OpenAI credentials
# AZURE_OPENAI_API_KEY=your_actual_key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### 4. Run the Applications

**Terminal 1 - Start MCP Server:**
```bash
python mcp_server.py
```

The server will start on `http://localhost:8000`

**Terminal 2 - Start Streamlit App:**
```bash
# Load environment variables
source .env  # On Windows: set -a; . .env; set +a

streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 🌐 Deployment

### Streamlit App (Streamlit Cloud)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add environment variables in Streamlit Cloud settings:
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`
   - `MCP_SERVER_URL` (your deployed MCP server URL)

### MCP Server Deployment Options

**Option 1: Cloud VM (Recommended)**
- Deploy on AWS EC2, Google Cloud, or Azure VM
- Install dependencies and run the MCP server
- Configure firewall to allow HTTP traffic
- Use a process manager like `systemd` or `supervisor`

**Option 2: Docker Container**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    texlive texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-mcp.txt .
RUN pip install --no-cache-dir -r requirements-mcp.txt

COPY mcp_server.py .
EXPOSE 8000

CMD ["python", "mcp_server.py"]
```

**Option 3: Heroku/Railway/Render**
- Create a `Procfile`: `web: python mcp_server.py`
- Add buildpacks for Python and FFmpeg
- Deploy through platform CLI or GitHub integration

## 📝 Usage Examples

### Example Prompts:

1. **Basic Shapes:**
   - "Create a circle that morphs into a square"
   - "Draw a triangle and rotate it 360 degrees"

2. **Mathematical Concepts:**
   - "Show the Pythagorean theorem with a visual proof"
   - "Animate the derivative of x squared"

3. **Advanced Animations:**
   - "Create a sine wave that transforms into a cosine wave"
   - "Visualize the Fourier transform of a square wave"

## 🔧 API Reference

### MCP Server Tools

#### `generate_animation(manim_code: str) -> dict`
Generates an animation from Manim code.

**Request:**
```json
{
  "manim_code": "from manim import *\n\nclass GeneratedScene(Scene):\n    def construct(self):\n        circle = Circle()\n        self.play(Create(circle))"
}
```

**Response:**
```json
{
  "success": true,
  "video_data": "base64_encoded_video...",
  "execution_time": 12.5,
  "video_size_bytes": 245678,
  "resolution": "480p"
}
```

#### `validate_manim_code(manim_code: str) -> dict`
Validates Manim code syntax without executing.

#### `get_server_status() -> dict`
Returns server status and configuration.

## 🛠️ Configuration

### Streamlit App (`streamlit_app.py`)
- Modify the system prompt in `generate_manim_code()` to adjust code generation behavior
- Adjust timeout values for API calls
- Customize UI theme in `.streamlit/config.toml`

### MCP Server (`mcp_server.py`)
- Change video quality: Modify `-ql` flag to `-qm` (medium) or `-qh` (high)
- Adjust timeout: Change `timeout=180` in subprocess.run()
- Customize output directory: Modify `self.temp_dir` in ManimExecutor

## 🐛 Troubleshooting

**Issue: "FFmpeg not found"**
- Solution: Install FFmpeg and ensure it's in your PATH

**Issue: "LaTeX not found" warnings**
- Solution: Install a LaTeX distribution (TeX Live, MiKTeX)
- Or avoid using Tex/MathTex in animations

**Issue: MCP Server connection failed**
- Check if MCP server is running
- Verify `MCP_SERVER_URL` in environment variables
- Check firewall/network settings

**Issue: Azure OpenAI API errors**
- Verify API key and endpoint are correct
- Check deployment name matches your Azure setup
- Ensure you have sufficient quota

## 📦 Project Structure

```
MCPproject/
├── streamlit_app.py           # Main Streamlit UI application
├── mcp_server.py              # FastMCP server for Manim execution
├── requirements-streamlit.txt # Streamlit app dependencies
├── requirements-mcp.txt       # MCP server dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file
├── .streamlit/
│   └── config.toml           # Streamlit configuration
└── README.md                  # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- [Manim Community](https://www.manim.community/) - Mathematical animation engine
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Streamlit](https://streamlit.io/) - Web app framework
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - LLM API

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review Manim documentation for animation-specific questions

---

**Built with ❤️ using Azure OpenAI, FastMCP, and Manim**
