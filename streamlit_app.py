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
    page_title="Visualize Your Imagination 🎬",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for educational theme
st.markdown("""
<style>
    /* Educational gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main content area */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Title styling */
    h1 {
        color: #667eea;
        text-align: center;
        font-weight: 700;
        padding-bottom: 1rem;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #764ba2;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Video container */
    .stVideo {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%);
        border-left: 4px solid #667eea;
        border-radius: 8px;
    }
    
    /* Success boxes */
    .stSuccess {
        background: linear-gradient(90deg, #e8f5e9 0%, #f1f8e9 100%);
        border-left: 4px solid #4caf50;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

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
if "enhanced_prompt" not in st.session_state:
    st.session_state.enhanced_prompt = None

# Detect environment and set appropriate server URL
def get_server_url():
    """Get the appropriate server URL based on environment."""
    # Check if running on Streamlit Cloud (production)
    # Streamlit Cloud sets HOSTNAME with 'streamlit' in it
    hostname = os.getenv("HOSTNAME", "")
    home = os.getenv("HOME", "")
    
    # If we're on Streamlit Cloud, use production server
    is_streamlit_cloud = (
        "streamlit" in hostname.lower() or
        "/home/appuser" in home or
        os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud"
    )
    
    if is_streamlit_cloud:
        # Use Azure Container Apps for production
        return "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"
    else:
        # Use local server for development
        return "http://localhost:8001"

MCP_SERVER_URL = get_server_url()

# Server status check
@st.cache_data(ttl=60)
def check_server_status(server_url: str) -> bool:
    """Check if the animation server is reachable."""
    try:
        resp = requests.get(f"{server_url}/status", timeout=10)
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

def enhance_user_prompt(user_input: str, client) -> str:
    """
    First step: Convert user's casual description into a detailed, 
    structured prompt optimized for python code generation.
    """
    
    enhancement_prompt = """
You are an expert prompt engineer for python animations.

Your job: Convert the user's casual description into a DETAILED, SPECIFIC prompt for python code generation.

IMPORTANT: LaTeX is NOT available. All math must use plain text with Unicode symbols.

Guidelines:
1. Break down complex ideas into 3-5 simple, sequential steps
2. Specify colors, sizes, and positions where helpful
3. Keep animations SHORT (5-15 seconds total)
4. Use simple shapes and text rather than complex graphics
5. For math/equations, ALWAYS use Unicode symbols: ×, ÷, ², ³, √, π, ∑, ∫, ≈, ≤, ≥, ∞, α, β, γ, Δ, etc.
6. NEVER suggest LaTeX, MathTex, or Tex - use Text() only
7. Describe visual elements clearly (circles, squares, arrows, text)
8. Avoid overly complex movements or transformations
9. Be concrete and specific about what should appear on screen

Example:
User: "gradient descent finding minimum"
Enhanced: "Create a simple parabola curve in blue. Show a red dot starting at a high point on the curve. Animate the dot moving down the curve in small steps, following the slope downward. Add a text label 'Gradient Descent' at the top. The dot should stop at the bottom (minimum) of the curve. Total duration: 8 seconds."

User: "explain E=mc²"
Enhanced: "Show the text 'E=mc²' in large font at center using Unicode superscript. Then split it into three parts: 'E' (energy) in yellow on left, '=' in white at center, 'mc²' (mass × speed²) in blue on right. Use arrows to show how mass times speed of light squared equals energy. Duration: 10 seconds."

User: "Pythagorean theorem"
Enhanced: "Show text 'a² + b² = c²' at top. Draw a right triangle with sides labeled 'a', 'b', and 'c'. Draw squares on each side. Use colors: red square on 'a', blue square on 'b', green square on 'c'. Animate showing that red area + blue area = green area. Duration: 12 seconds."

Now convert this user input into a detailed, specific python animation prompt:
"""
    
    try:
        response = client.chat.completions.create(
            model=st.session_state.azure_deployment,
            messages=[
                {"role": "system", "content": enhancement_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.8,
            max_tokens=800,
            timeout=30,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # If enhancement fails, return original input
        st.warning(f"⚠️ Prompt enhancement skipped: {str(e)}")
        return user_input

def generate_manim_code(enhanced_prompt: str, client) -> str:
    """
    Second step: Generate python code from the enhanced, detailed prompt.
    """

    system_prompt = """
You are a Manim code generator. Generate clean, working Python code.

⚠️ CRITICAL: LaTeX is NOT installed. You MUST NOT use MathTex() or Tex() at all.

MANDATORY RULES:
1. Output ONLY executable Python code (no markdown, no ```python blocks, no explanations)
2. Always start with: from manim import *
3. Class must be named: GeneratedScene(Scene)
4. Use construct(self) method
5. Keep it SIMPLE - prefer basic shapes and text

FOR TEXT (REQUIRED FOR ALL TEXT/MATH):
- Use Text("message", font_size=36, color=WHITE) for ALL text
- Use Unicode symbols for math: ×, ÷, ², ³, √, π, ∑, ∫, ≈, ≤, ≥, ∞
- Examples: Text("E=mc²"), Text("a² + b² = c²"), Text("∫ f(x)dx")
- NEVER use MathTex() or Tex() - they will fail without LaTeX

FOR SHAPES:
- Circle(), Square(), Rectangle(), Line(), Arrow(), Dot(), Polygon()
- Set color: Circle(color=BLUE, radius=1)
- Set position: .shift(UP), .move_to(ORIGIN), .next_to(other, RIGHT)

FOR ANIMATIONS:
- self.play(Write(text)) - for text appearing
- self.play(Create(shape)) - for shapes appearing
- self.play(FadeIn(object)) - fade in
- self.play(FadeOut(object)) - fade out
- self.play(object.animate.shift(UP)) - move object
- self.play(Transform(obj1, obj2)) - morph objects
- self.wait(1) - pause for 1 second

BEST PRACTICES:
- Define ALL objects before using them in animations
- Use clear variable names
- Keep total animation under 15 seconds
- Break complex ideas into 3-5 simple steps
- Test each object is created before animating it

GOOD EXAMPLE:
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Using Unicode for math
        title = Text("E=mc²", font_size=48, color=YELLOW)
        formula = Text("Energy = Mass × Speed²", font_size=36)
        formula.next_to(title, DOWN)
        
        self.play(Write(title))
        self.wait(0.5)
        self.play(FadeIn(formula))
        self.wait(1)

BAD EXAMPLE (DON'T DO THIS):
- equation = MathTex(r"E=mc^2")  # ❌ FORBIDDEN - LaTeX not installed
- tex = Tex("Hello")  # ❌ FORBIDDEN - LaTeX not installed
"""

    try:
        response = client.chat.completions.create(
            model=st.session_state.azure_deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create this animation:\n{enhanced_prompt}"},
            ],
            temperature=0.5,
            max_tokens=2500,
            timeout=60,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Code generation failed: {str(e)}")

def call_mcp_server(manim_code: str) -> dict:
    """Call the Azure Container Apps server to generate animation."""
    
    # Direct REST API call to Azure Container Apps
    url = f"{MCP_SERVER_URL}/generate_animation"
    
    try:
        payload = {"manim_code": manim_code}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=300)  # 5 minutes
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": f"Server error ({response.status_code}): {response.text}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }

def main():
    st.title("🎬 Visualize Your Imagination")
    st.markdown('<p class="subtitle">✨ Transform your ideas into stunning mathematical animations with AI</p>', unsafe_allow_html=True)
    
    # Sidebar for Azure credentials - collapsed by default
    with st.sidebar:
        st.markdown("### 🤖 AI Configuration")
        st.caption("Enter LLM API credentials here")
        
        with st.expander("🔑 Azure OpenAI Credentials", expanded=False):
            st.session_state.azure_api_key = st.text_input(
                "Azure API Key",
                value=st.session_state.azure_api_key,
                type="password",
            )
            
            st.session_state.azure_endpoint = st.text_input(
                "Azure Endpoint",
                value=st.session_state.azure_endpoint,
            )
            
            st.session_state.azure_deployment = st.text_input(
                "Deployment Name",
                value=st.session_state.azure_deployment,
            )
            
            st.session_state.azure_api_version = st.text_input(
                "API Version",
                value=st.session_state.azure_api_version,
            )
        
        st.markdown("---")
        st.success("✅ AI-Enhanced Generation")
        st.caption("Smart prompts • Better code • Faster results")
        
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")
        st.markdown("""
        - Describe animations in simple terms
        - Mention colors and shapes
        - Keep it short (5-15 seconds)
        - Use Unicode for math: ², π, √
        """)
    
    # Create two-column layout: input left, video right
    left_col, right_col = st.columns([1, 1])
    
    # Left column: Input and enhanced prompt
    with left_col:
        st.markdown("### 📝 Your Animation Idea")
        user_input = st.text_area(
            "Describe what you want to animate:",
            placeholder="Example: Show a blue circle morphing into a red square, then rotating 360 degrees with a smooth transition",
            height=180,
            label_visibility="collapsed"
        )
        
        # Show enhanced prompt if available
        if st.session_state.enhanced_prompt:
            st.markdown("#### ✨ AI-Enhanced Prompt")
            st.info(st.session_state.enhanced_prompt)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            generate_button = st.button("🎨 Generate Animation", type="primary", use_container_width=True)
        with col2:
            if st.session_state.generated_video:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.generated_video = None
                    st.session_state.generated_code = None
                    st.session_state.last_prompt = ""
                    st.session_state.execution_time = None
                    st.session_state.enhanced_prompt = None
                    st.rerun()
    
    # Right column: Video display
    with right_col:
        if st.session_state.generated_video:
            st.markdown("### 🎬 Your Animation")
            st.video(st.session_state.generated_video)
            
            st.download_button(
                "📥 Download MP4",
                data=st.session_state.generated_video,
                file_name=f"animation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
            
            if st.session_state.execution_time:
                st.success(f"⏱️ Generated in {st.session_state.execution_time}s")
            
            with st.expander("🐍 View Python Code for Animation"):
                st.code(st.session_state.generated_code, language="python")
        else:
            st.markdown("### 🎬 Preview")
            st.info("👈 Enter your animation idea on the left and click Generate to see it come to life here!")
            
            # Example placeholder
            st.markdown("""
            **Example animations you can create:**
            - Mathematical visualizations (Pythagorean theorem, derivatives)
            - Geometric transformations and morphing
            - Physics simulations (pendulum, waves)
            - Data visualizations and charts
            - Educational concept explanations
            """)
    
    # Check if credentials are configured
    if not (st.session_state.azure_api_key and st.session_state.azure_endpoint and st.session_state.azure_deployment):
        st.warning("⚠️ Please configure Azure OpenAI credentials in the sidebar to proceed.")
        return
    
    if generate_button and user_input:
        # Validate Azure credentials
        if not all([
            st.session_state.azure_api_key,
            st.session_state.azure_endpoint,
            st.session_state.azure_deployment,
        ]):
            st.error("❌ Azure OpenAI credentials are incomplete")
            return
        
        # Get Azure client
        client = get_azure_client(
            st.session_state.azure_api_key,
            st.session_state.azure_endpoint,
            st.session_state.azure_api_version,
        )

        # Step 1: Enhance the user's prompt
        try:
            with st.spinner("🔍 Step 1/3: Analyzing and enhancing your prompt..."):
                enhanced_prompt = enhance_user_prompt(user_input, client)
                st.session_state.enhanced_prompt = enhanced_prompt
                
        except Exception as e:
            st.error(f"❌ Failed to enhance prompt: {str(e)}")
            st.info("💡 Check your Azure OpenAI credentials")
            return

        # Step 2: Generate Manim code from enhanced prompt
        try:
            with st.spinner("🤖 Step 2/3: Generating python code..."):
                manim_code = generate_manim_code(enhanced_prompt, client)
                
            # Clean the code if it's wrapped in markdown
            if "```python" in manim_code:
                manim_code = manim_code.split("```python")[1].split("```")[0].strip()
            elif "```" in manim_code:
                manim_code = manim_code.split("```")[1].split("```")[0].strip()
                
        except Exception as e:
            st.error(f"❌ Failed to generate code: {str(e)}")
            st.info("💡 Try simplifying your prompt or check your Azure OpenAI credentials")
            return

        # Step 3: Render the animation
        with st.spinner("🎬 Step 3/3: Rendering animation (up to 5 minutes for complex scenes)..."):
            try:
                result = call_mcp_server(manim_code)
            except Exception as e:
                st.error(f"❌ Rendering failed: {str(e)}")
                st.info("💡 The animation might be too complex or contain errors")
                with st.expander("📝 Show Generated Code"):
                    st.code(manim_code, language="python")
                return

        # Show any warnings
        if result.get("warnings"):
            for warning in result["warnings"]:
                st.warning(f"⚠️ {warning}")

        if result.get("success"):
            st.session_state.generated_code = manim_code
            st.session_state.last_prompt = user_input
            st.session_state.execution_time = result.get("execution_time")

            st.session_state.generated_video = base64.b64decode(
                result["video_data"]
            )

            st.success("✅ Animation generated successfully")
            st.rerun()
        else:
            error_msg = result.get("error", "Unknown error")
            st.error(f"❌ Animation generation failed")
            
            # Show detailed error in expander
            with st.expander("🔍 Error Details", expanded=True):
                st.code(error_msg, language="text")
                
            # Show the generated code for debugging
            with st.expander("📝 Generated Code (for debugging)"):
                st.code(manim_code, language="python")
                
            st.info("💡 Tips: Try a simpler prompt, or check if the code has syntax errors")
    
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #667eea; font-weight: 500;">⚡ Powered by Azure AI • Manim Engine • Educational Excellence</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
