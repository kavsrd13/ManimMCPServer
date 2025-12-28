import streamlit as st
import os
from openai import AzureOpenAI
import requests
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="See your Imagination come to Life🎬",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state for credentials
if "azure_api_key" not in st.session_state:
    st.session_state.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
if "azure_endpoint" not in st.session_state:
    st.session_state.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
if "azure_deployment" not in st.session_state:
    st.session_state.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
if "azure_api_version" not in st.session_state:
    st.session_state.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# MCP Server Base URL - Azure Container Apps deployment
MCP_SERVER_URL = "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"

# Common headers for MCP JSON-RPC and REST calls
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

# Helper: parse possible SSE (Server-Sent Events) or JSON responses
def parse_mcp_response(response):
    try:
        content_type = response.headers.get("Content-Type", "")
        # Prefer streaming parser for SSE
        if "text/event-stream" in content_type:
            result_obj = None
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if not data_str:
                        continue
                    try:
                        obj = json.loads(data_str)
                        if isinstance(obj, dict):
                            # JSON-RPC result shape
                            if "result" in obj and isinstance(obj["result"], dict):
                                result_obj = obj["result"]
                            else:
                                result_obj = obj
                    except Exception:
                        continue
            return result_obj
        # Fallback: non-streamed SSE payload in body
        body = response.text or ""
        if "data:" in body:
            result_obj = None
            for line in body.splitlines():
                l = line.strip()
                if l.startswith("data:"):
                    data_str = l[5:].strip()
                    if not data_str:
                        continue
                    try:
                        obj = json.loads(data_str)
                        if isinstance(obj, dict):
                            result_obj = obj.get("result", obj)
                    except Exception:
                        continue
            if result_obj is not None:
                return result_obj
        # Otherwise, attempt JSON
        return response.json()
    except Exception:
        return None

# MCP server status check (tries multiple endpoints)
@st.cache_data(ttl=60)
def check_mcp_status() -> bool:
    endpoints = [
        f"{MCP_SERVER_URL}/status",
        f"{MCP_SERVER_URL}/mcp/status",
        f"{MCP_SERVER_URL}/",
        f"{MCP_SERVER_URL}/mcp",
    ]
    for url in endpoints:
        try:
            # First try GET
            resp = requests.get(url, timeout=10, headers={"Accept": "application/json, text/event-stream"})
            if resp.status_code == 200:
                return True
            # Then try JSON-RPC status via POST when path looks like MCP
            if url.endswith("/mcp") or url.endswith("/mcp/status"):
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "get_server_status",
                        "arguments": {}
                    }
                }
                resp = requests.post(url, json=payload, headers=DEFAULT_HEADERS, timeout=10, stream=True)
                if resp.status_code == 200:
                    data = parse_mcp_response(resp)
                    if isinstance(data, dict):
                        if "success" in data or "result" in data:
                            return True
        except requests.exceptions.RequestException:
            continue
    return False

# Get Azure client with credentials from session state
@st.cache_resource
def get_azure_client(api_key, endpoint, api_version):
    return AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )

def generate_manim_code(user_prompt: str, client) -> str:
    """Convert natural language to Manim code using Azure OpenAI."""
    
    system_prompt = """You are an expert in Manim (Mathematical Animation Engine).
Convert the user's natural language description into valid Manim code.
Your code should:
- Be a complete, runnable Python class that inherits from Scene
- Use Manim Community Edition (manim) syntax
- Include proper imports
- Have a class named 'GeneratedScene' that inherits from Scene
- Implement the construct() method
- Be well-commented and follow best practices
- Use appropriate animations and timing

Return ONLY the Python code, no explanations or markdown formatting."""

    try:
        response = client.chat.completions.create(
            model=st.session_state.azure_deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating Manim code: {str(e)}")
        return None

def call_mcp_server(manim_code: str) -> dict:
    """Call the MCP Manim server to generate animation."""
    
    endpoints = [
        f"{MCP_SERVER_URL}/generate_animation",
        f"{MCP_SERVER_URL}/mcp/generate_animation",
        f"{MCP_SERVER_URL}/tools/generate_animation",
        f"{MCP_SERVER_URL}/mcp/tools/generate_animation",
        f"{MCP_SERVER_URL}/mcp",
        f"{MCP_SERVER_URL}/mcp/rpc",
    ]

    last_exception = None
    for url in endpoints:
        try:
            # Try common payload shapes
            is_mcp = "/mcp" in url
            if is_mcp:
                payloads = [
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "generate_animation",
                            "arguments": {"manim_code": manim_code}
                        }
                    }
                ]
            else:
                payloads = [
                    {"manim_code": manim_code},
                    {"arguments": {"manim_code": manim_code}},
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "generate_animation",
                            "arguments": {"manim_code": manim_code}
                        }
                    },
                ]
            for payload in payloads:
                # Use JSON-RPC headers when payload includes jsonrpc
                headers = DEFAULT_HEADERS if ("jsonrpc" in payload or is_mcp) else {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
                response = requests.post(url, json=payload, headers=headers, timeout=120, stream=True)

                if response.status_code == 200:
                    data = parse_mcp_response(response)
                    # Handle direct REST shape
                    if isinstance(data, dict) and ("success" in data or "video_data" in data or "video_url" in data):
                        return data
                    # Handle JSON-RPC shape
                    if isinstance(data, dict) and "result" in data and isinstance(data["result"], dict):
                        return data["result"]
                    # Unknown success shape; return raw
                    return data
                elif response.status_code == 404:
                    # Try next endpoint or payload variant
                    continue
                elif response.status_code in (405, 400, 406, 415):
                    # Method not allowed / bad request -> try next variant
                    continue
                else:
                    # If not 404, surface the error and stop
                    st.error(f"MCP Server Error ({url}): {response.text}")
                    return None
        except requests.exceptions.RequestException as e:
            last_exception = e
            # Try next endpoint variant
            continue

    if last_exception:
        st.error(f"Error connecting to MCP server: {str(last_exception)}")
    else:
        st.error("MCP Server Error: No matching endpoint found.")
    return None

def main():
    st.title("🎬 Visualize Your Imagination")
    st.markdown("### Create stunning animations from your ideas!")
    
    # Sidebar for Azure credentials
    with st.sidebar:
        st.header("🔑 Azure OpenAI Credentials")
        st.markdown("**Enter your Azure OpenAI API details**")
        
        st.session_state.azure_api_key = st.text_input(
            "Azure API Key",
            value=st.session_state.azure_api_key,
            type="password",
            help="Your Azure OpenAI API key"
        )
        
        st.session_state.azure_endpoint = st.text_input(
            "Azure Endpoint",
            value=st.session_state.azure_endpoint,
            placeholder="https://your-resource.openai.azure.com/",
            help="Your Azure OpenAI endpoint URL"
        )
        
        st.session_state.azure_deployment = st.text_input(
            "Deployment Name",
            value=st.session_state.azure_deployment,
            placeholder="gpt-4",
            help="Your model deployment name"
        )
        
        st.session_state.azure_api_version = st.text_input(
            "API Version",
            value=st.session_state.azure_api_version,
            placeholder="2024-12-01-preview",
            help="Azure OpenAI API version"
        )
        
        st.markdown("---")
        
        # Configuration status
        api_configured = bool(st.session_state.azure_api_key and st.session_state.azure_endpoint and st.session_state.azure_deployment)
        
        st.write(f"**Azure OpenAI:** {'✅ Configured' if api_configured else '❌ Not configured'}")
        mcp_connected = check_mcp_status()
        st.write(f"**MCP Server:** {'✅ Connected' if mcp_connected else '❌ Not reachable'}")
        st.markdown(f"*Server: {MCP_SERVER_URL}*")
        
        st.markdown("---")
        st.header("📚 Examples")
        st.markdown("""
        - Create a circle that transforms into a square
        - Show the Pythagorean theorem with animation
        - Animate a sine wave transformation
        - Display mathematical equation solving steps
        """)
    
    # Main input area
    user_input = st.text_area(
        "Describe the animation you want to create:",
        placeholder="Example: Create an animation showing a circle transforming into a square, then rotating 360 degrees",
        height=150
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_button = st.button("🎨 Generate Animation", type="primary")
    
    # Check if credentials are configured
    if not (st.session_state.azure_api_key and st.session_state.azure_endpoint and st.session_state.azure_deployment):
        st.warning("⚠️ Please configure Azure OpenAI credentials in the sidebar to proceed.")
        return
    
    if generate_button and user_input:
        try:
            # Initialize Azure client with user credentials
            client = get_azure_client(
                st.session_state.azure_api_key,
                st.session_state.azure_endpoint,
                st.session_state.azure_api_version
            )
            
            # Step 1: Generate Manim code
            with st.spinner("🤖 Converting your description to Manim code..."):
                manim_code = generate_manim_code(user_input, client)
            
            if manim_code:
                # Display generated code
                with st.expander("📝 View Generated Manim Code", expanded=False):
                    st.code(manim_code, language="python")
                
                # Step 2: Generate animation via MCP server
                with st.spinner("🎬 Generating animation... This may take a minute..."):
                    result = call_mcp_server(manim_code)
                
                if result and result.get("success"):
                    st.success("✅ Animation generated successfully!")
                    
                    # Display the video
                    if "video_data" in result:
                        video_bytes = base64.b64decode(result["video_data"])
                        st.video(video_bytes)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Animation",
                            data=video_bytes,
                            file_name=f"manim_animation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                            mime="video/mp4"
                        )
                    elif "video_url" in result:
                        st.video(result["video_url"])
                    
                    # Show execution info
                    if "execution_time" in result:
                        st.info(f"⏱️ Generation time: {result['execution_time']:.2f} seconds")
                else:
                    st.error("❌ Failed to generate animation. Check the logs for details.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    elif generate_button:
        st.warning("⚠️ Please enter a description for your animation.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p style='color: #888;'>✨ Bring your ideas to life with AI-powered animations</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
