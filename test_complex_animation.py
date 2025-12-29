"""
Test Complex Animation Generation
Tests the full pipeline with a complex animation prompt
"""
import os
from openai import AzureOpenAI
import requests
from dotenv import load_dotenv
import base64

load_dotenv()

print("=" * 70)
print("TESTING COMPLEX ANIMATION GENERATION")
print("=" * 70)

# Setup
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
server_url = "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=endpoint
)

# Test with a complex prompt
test_prompts = [
    {
        "name": "Pythagorean Theorem",
        "prompt": "Show the Pythagorean theorem: a² + b² = c² with a visual proof using a right triangle and squares on each side"
    },
    {
        "name": "Gradient Descent",
        "prompt": "Explain gradient descent: show a ball rolling down a parabolic curve to find the minimum point"
    },
    {
        "name": "Sorting Animation",
        "prompt": "Show bubble sort with 5 colored bars that swap positions to sort from smallest to largest"
    }
]

# Let user choose
print("\nAvailable test prompts:")
for i, p in enumerate(test_prompts, 1):
    print(f"{i}. {p['name']}: {p['prompt']}")

choice = input("\nSelect prompt (1-3) or press Enter for #1: ").strip() or "1"
selected = test_prompts[int(choice) - 1]

user_prompt = selected["prompt"]
print(f"\n{'='*70}")
print(f"Testing: {selected['name']}")
print(f"Prompt: {user_prompt}")
print(f"{'='*70}")

# Step 1: Enhance prompt
print("\n[1/3] Enhancing prompt with AI...")
enhancement_system = """
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
            {"role": "system", "content": enhancement_system},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=800,
        timeout=30,
    )
    enhanced_prompt = response.choices[0].message.content.strip()
    print(f"✓ Enhanced prompt:\n{enhanced_prompt}\n")
except Exception as e:
    print(f"✗ Enhancement failed: {e}")
    exit(1)

# Step 2: Generate code
print("[2/3] Generating Python code...")
code_system = """
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
"""

try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": code_system},
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
    
    print(f"✓ Generated code ({len(manim_code)} characters)")
    print(f"\nCODE PREVIEW:")
    print("-" * 70)
    print(manim_code)
    print("-" * 70)
    
except Exception as e:
    print(f"✗ Code generation failed: {e}")
    exit(1)

# Step 3: Render animation
print("\n[3/3] Rendering animation (this may take 1-5 minutes)...")
try:
    payload = {"manim_code": manim_code}
    response = requests.post(
        f"{server_url}/generate_animation",
        json=payload,
        timeout=300  # 5 minutes
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✓ Animation rendered successfully!")
            print(f"  - Execution time: {result.get('execution_time'):.2f}s")
            print(f"  - Video size: {len(result.get('video_data', '')) / 1024:.1f} KB")
            
            # Save video
            video_data = base64.b64decode(result["video_data"])
            output_file = f"test_{selected['name'].replace(' ', '_').lower()}.mp4"
            with open(output_file, "wb") as f:
                f.write(video_data)
            print(f"  - Saved to: {output_file}")
            
            if result.get("warnings"):
                print("\nWarnings:")
                for warning in result["warnings"]:
                    print(f"  ⚠️ {warning}")
                    
        else:
            print(f"✗ Rendering failed!")
            print(f"\nERROR MESSAGE:")
            print(result.get("error", "Unknown error"))
            print(f"\nGENERATED CODE:")
            print(manim_code)
            exit(1)
    else:
        print(f"✗ Server error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        exit(1)
        
except requests.exceptions.Timeout:
    print("✗ Request timed out after 5 minutes")
    print("The animation might be too complex. Try simplifying the prompt.")
    exit(1)
except Exception as e:
    print(f"✗ Rendering request failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("✅ COMPLEX ANIMATION TEST PASSED!")
print("=" * 70)
print(f"\nYour animation is ready: {output_file}")
print("You can open it with any video player.")
