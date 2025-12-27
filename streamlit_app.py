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

# Initialize Azure OpenAI client
@st.cache_resource
def get_azure_client():
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

def generate_manim_code(user_prompt: str) -> str:
    """Convert natural language to Manim code using Azure OpenAI."""
    client = get_azure_client()
    
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
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
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
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    try:
        response = requests.post(
            f"{mcp_server_url}/generate_animation",
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
    
    # Sidebar for configuration status
    with st.sidebar:
        st.header("⚙️ Configuration")
        azure_configured = bool(os.getenv("AZURE_OPENAI_API_KEY"))
        mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
        
        st.write(f"**Azure OpenAI:** {'✅ Configured' if azure_configured else '❌ Not configured'}")
        st.write(f"**MCP Server:** {mcp_url}")
        
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
    
    if generate_button and user_input:
        # Step 1: Generate Manim code
        with st.spinner("🤖 Converting your description to Manim code..."):
            manim_code = generate_manim_code(user_input)
        
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
