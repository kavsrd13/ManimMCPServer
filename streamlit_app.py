import streamlit as st
import os
from openai import AzureOpenAI
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Manim Animation Generator",
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

# Fixed MCP Server URL (FastMCP Cloud)
MCP_SERVER_URL = "https://independent-maroon-puffin.fastmcp.app/mcp"

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
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/generate_animation",
            json={"manim_code": manim_code},
            timeout=120  # 2 minutes timeout for video generation
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"MCP Server Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to MCP server: {str(e)}")
        return None

def main():
    st.title("🎬 Manim Animation Generator")
    st.markdown("### Create mathematical animations from natural language!")
    
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
        st.write(f"**MCP Server:** ✅ Connected")
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
            <p>Powered by Azure OpenAI + FastMCP + Manim</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
