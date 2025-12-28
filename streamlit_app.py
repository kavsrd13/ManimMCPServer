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
if "generated_video" not in st.session_state:
    st.session_state.generated_video = None
if "generated_code" not in st.session_state:
    st.session_state.generated_code = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "execution_time" not in st.session_state:
    st.session_state.execution_time = None

# Azure Container Apps server base URL
MCP_SERVER_URL = "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"

# Server status check
@st.cache_data(ttl=60)
def check_server_status() -> bool:
    """Check if the Azure Container Apps server is reachable."""
    try:
        resp = requests.get(f"{MCP_SERVER_URL}/status", timeout=10)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
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
    """Call the Azure Container Apps Manim server to generate animation."""
    
    # Direct REST API call to Azure Container Apps
    url = f"{MCP_SERVER_URL}/generate_animation"
    
    try:
        payload = {"manim_code": manim_code}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Server Error ({response.status_code}): {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to server: {str(e)}")
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
        server_connected = check_server_status()
        st.write(f"**Animation Server:** {'✅ Connected' if server_connected else '❌ Not reachable'}")
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
    
    col1, col2, col3 = st.columns([2, 1, 3])
    with col1:
        generate_button = st.button("🎨 Generate Animation", type="primary")
    with col2:
        if st.session_state.generated_video:
            if st.button("🗑️ Clear"):
                st.session_state.generated_video = None
                st.session_state.generated_code = None
                st.session_state.last_prompt = ""
                st.session_state.execution_time = None
                st.rerun()
    
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
                # Step 2: Generate animation via server
                with st.spinner("🎬 Generating animation... This may take a minute..."):
                    result = call_mcp_server(manim_code)
                
                if result and result.get("success"):
                    # Store in session state
                    st.session_state.generated_code = manim_code
                    st.session_state.last_prompt = user_input
                    st.session_state.execution_time = result.get("execution_time")
                    
                    if "video_data" in result:
                        st.session_state.generated_video = base64.b64decode(result["video_data"])
                    elif "video_url" in result:
                        st.session_state.generated_video = result["video_url"]
                    
                    st.success("✅ Animation generated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate animation")
                    # Show detailed error information
                    if result:
                        if "error" in result:
                            st.error(f"**Error:** {result['error']}")
                        if "stderr" in result:
                            with st.expander("🔍 View Error Details"):
                                st.code(result.get("stderr", "No stderr available"), language="text")
                        if "stdout" in result:
                            with st.expander("📄 View Output"):
                                st.code(result.get("stdout", "No stdout available"), language="text")
                    else:
                        st.error("No response received from the animation server. Please try again.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            with st.expander("🔍 View Full Error Trace"):
                st.code(traceback.format_exc(), language="text")
    
    elif generate_button:
        st.warning("⚠️ Please enter a description for your animation.")
    
    # Display generated video if available
    if st.session_state.generated_video:
        st.markdown("---")
        st.markdown("### 🎬 Generated Animation")
        
        if st.session_state.last_prompt:
            st.info(f"**Prompt:** {st.session_state.last_prompt}")
        
        # Display generated code
        if st.session_state.generated_code:
            with st.expander("📝 View Generated Manim Code", expanded=False):
                st.code(st.session_state.generated_code, language="python")
        
        # Display the video
        if isinstance(st.session_state.generated_video, bytes):
            st.video(st.session_state.generated_video)
            
            # Download button
            st.download_button(
                label="📥 Download Animation",
                data=st.session_state.generated_video,
                file_name=f"manim_animation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                mime="video/mp4",
                key="download_video"
            )
        else:
            st.video(st.session_state.generated_video)
        
        # Show execution info
        if st.session_state.execution_time:
            st.info(f"⏱️ Generation time: {st.session_state.execution_time:.2f} seconds")
    
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
