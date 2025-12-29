"""
Debug Streamlit Animation Failure
This script helps diagnose what's causing the "Manim execution failed" error
"""
import os
from openai import AzureOpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("DEBUGGING STREAMLIT ANIMATION FAILURE")
print("=" * 70)

# Get your prompt
print("\nWhat prompt did you try in the Streamlit app?")
print("(Press Enter to use a test prompt)")
user_prompt = input("\nYour prompt: ").strip()

if not user_prompt:
    user_prompt = "Create a blue circle"
    print(f"Using test prompt: {user_prompt}")

# Setup
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
server_url = "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"

print(f"\n{'='*70}")
print(f"Testing prompt: {user_prompt}")
print(f"{'='*70}")

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=endpoint
)

# Step 1: Enhance prompt (same as Streamlit)
print("\n[1/3] Enhancing prompt...")
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

Now convert this user input into a detailed, specific python animation prompt:
"""

try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": enhancement_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=800,
        timeout=30,
    )
    enhanced_prompt = response.choices[0].message.content.strip()
    print(f"✓ Enhanced: {enhanced_prompt[:200]}...")
except Exception as e:
    print(f"✗ Enhancement failed: {e}")
    enhanced_prompt = user_prompt

# Step 2: Generate code (same as Streamlit)
print("\n[2/3] Generating Manim code...")
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
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create this animation:\n{enhanced_prompt}"},
        ],
        temperature=0.5,
        max_tokens=2500,
        timeout=60,
    )
    manim_code = response.choices[0].message.content.strip()
    
    # Clean code
    if "```python" in manim_code:
        manim_code = manim_code.split("```python")[1].split("```")[0].strip()
    elif "```" in manim_code:
        manim_code = manim_code.split("```")[1].split("```")[0].strip()
    
    print(f"✓ Generated {len(manim_code)} characters of code")
    print("\nGENERATED CODE:")
    print("-" * 70)
    print(manim_code)
    print("-" * 70)
    
except Exception as e:
    print(f"✗ Code generation failed: {e}")
    exit(1)

# Step 3: Send to server and get DETAILED error
print("\n[3/3] Sending to animation server...")
print("⏱️  Waiting for response...")

try:
    payload = {"manim_code": manim_code}
    response = requests.post(
        f"{server_url}/generate_animation",
        json=payload,
        timeout=300
    )
    
    print(f"\nServer Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("success"):
            print("\n✅ SUCCESS! Animation rendered without errors.")
            print(f"   Execution time: {result.get('execution_time')}s")
            print(f"   Video size: {len(result.get('video_data', '')) / 1024:.1f} KB")
            print("\n✓ The prompt works! The issue might be temporary.")
        else:
            print("\n❌ MANIM EXECUTION FAILED")
            print("\n" + "="*70)
            print("DETAILED ERROR MESSAGE:")
            print("="*70)
            error = result.get('error', 'No error message provided')
            print(error)
            print("="*70)
            
            # Analyze the error
            print("\n🔍 ERROR ANALYSIS:")
            if "MathTex" in error or "Tex(" in error:
                print("  ⚠️  LaTeX Error: Code uses MathTex or Tex (not allowed)")
                print("  💡 Fix: Ask for simpler prompt or retry generation")
            elif "NameError" in error:
                print("  ⚠️  Name Error: Variable used before definition")
                print("  💡 Fix: Try a simpler prompt")
            elif "AttributeError" in error:
                print("  ⚠️  Attribute Error: Invalid Manim method/property")
                print("  💡 Fix: Simplify the prompt or retry")
            elif "TypeError" in error:
                print("  ⚠️  Type Error: Wrong parameter type")
                print("  💡 Fix: Retry or simplify prompt")
            elif "SyntaxError" in error:
                print("  ⚠️  Syntax Error: Invalid Python code generated")
                print("  💡 Fix: Retry generation")
            else:
                print("  ⚠️  Unknown error type")
                print("  💡 Fix: Try a much simpler prompt")
            
            print("\n📝 SUGGESTED ACTIONS:")
            print("  1. Try a simpler prompt: 'Create a blue circle'")
            print("  2. Avoid complex math formulas")
            print("  3. Avoid advanced animations")
            print("  4. Check the generated code for MathTex/Tex usage")
            
    else:
        print(f"\n❌ SERVER ERROR: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("\n❌ Request timed out after 5 minutes")
except Exception as e:
    print(f"\n❌ Request failed: {e}")

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)
