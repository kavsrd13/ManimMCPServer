"""
Super Complex Animation Test
Tests an extremely complex prompt combining multiple concepts
"""
import os
from openai import AzureOpenAI
import requests
from dotenv import load_dotenv
import base64

load_dotenv()

print("=" * 70)
print("SUPER COMPLEX ANIMATION TEST")
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

# Super complex prompts
super_complex_prompts = [
    {
        "name": "Neural Network Forward Pass",
        "prompt": """
        Create an animation showing a simple neural network with 3 layers:
        - Input layer: 3 blue circles labeled x₁, x₂, x₃
        - Hidden layer: 4 green circles labeled h₁, h₂, h₃, h₄
        - Output layer: 2 red circles labeled y₁, y₂
        
        Show the forward pass with:
        1. Lines connecting all inputs to hidden layer nodes
        2. Highlight connections one by one as data flows through
        3. Each node lights up when it receives data
        4. Show activation flowing from input → hidden → output
        5. Add text "Forward Pass" at top and "σ(Wx + b)" formula
        Duration: 15 seconds
        """
    },
    {
        "name": "Fourier Series Approximation",
        "prompt": """
        Show how Fourier series approximates a square wave:
        1. Draw a square wave in black
        2. Start with first harmonic (sine wave) in red
        3. Add 3rd harmonic in blue, show sum in purple
        4. Add 5th harmonic in green, show sum in orange
        5. Final approximation should look closer to square wave
        6. Show formula: f(x) = Σ (4/nπ)sin(nx) for odd n
        7. Label each step: "n=1", "n=1,3", "n=1,3,5"
        Duration: 18 seconds
        """
    },
    {
        "name": "Binary Search Tree Insertion",
        "prompt": """
        Animate inserting numbers into a binary search tree:
        1. Start with empty tree, show "Insert: 50, 30, 70, 20, 40, 60, 80"
        2. Insert 50 as root (circle with "50" inside)
        3. Insert 30 to left of 50 (with line connecting)
        4. Insert 70 to right of 50 (with line connecting)
        5. Continue with remaining numbers
        6. Highlight the comparison path for each insertion
        7. Show final balanced tree structure
        8. Add labels "Left: smaller" and "Right: larger"
        Duration: 20 seconds
        """
    },
    {
        "name": "Matrix Multiplication Visualization",
        "prompt": """
        Show matrix multiplication A × B = C where:
        - A is 2×3 matrix with values [[1,2,3], [4,5,6]]
        - B is 3×2 matrix with values [[7,8], [9,10], [11,12]]
        
        Animate:
        1. Show matrices A and B side by side
        2. Highlight first row of A and first column of B
        3. Show dot product: 1×7 + 2×9 + 3×11 = 58
        4. Place 58 in position C[0,0]
        5. Repeat for remaining elements
        6. Show final result matrix C
        7. Add formula: (AB)ᵢⱼ = Σₖ AᵢₖBₖⱼ
        Duration: 25 seconds
        """
    }
]

print("\nAvailable super complex prompts:")
for i, p in enumerate(super_complex_prompts, 1):
    print(f"\n{i}. {p['name']}")
    print(f"   {p['prompt'][:150]}...")

choice = input("\n\nSelect prompt (1-4) or press Enter for #1: ").strip() or "1"
selected = super_complex_prompts[int(choice) - 1]

user_prompt = selected["prompt"]
print(f"\n{'='*70}")
print(f"Testing: {selected['name']}")
print(f"{'='*70}")

# Step 1: Enhance prompt
print("\n[1/3] Enhancing prompt with AI...")
enhancement_system = """
You are an expert prompt engineer for python animations.

Your job: Convert the user's casual description into a DETAILED, SPECIFIC prompt for python code generation.

IMPORTANT: LaTeX is NOT available. All math must use plain text with Unicode symbols.

Guidelines:
1. Break down complex ideas into clear sequential steps
2. Specify colors, sizes, and positions precisely
3. Keep animations under 30 seconds for complex ones
4. Use simple shapes and text rather than complex graphics
5. For math/equations, ALWAYS use Unicode symbols: ×, ÷, ², ³, √, π, ∑, ∫, ≈, ≤, ≥, ∞, α, β, γ, Δ, σ, Σ
6. NEVER suggest LaTeX, MathTex, or Tex - use Text() only
7. Describe visual elements clearly (circles, squares, arrows, text)
8. For very complex animations, prioritize clarity over completeness
9. Suggest pauses between major steps

Now convert this user input into a detailed, specific python animation prompt:
"""

try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": enhancement_system},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=30,
    )
    enhanced_prompt = response.choices[0].message.content.strip()
    print(f"✓ Enhanced prompt ({len(enhanced_prompt)} chars)")
    print(f"\n{enhanced_prompt}\n")
except Exception as e:
    print(f"✗ Enhancement failed: {e}")
    exit(1)

# Step 2: Generate code
print("[2/3] Generating Python code...")
code_system = """
You are a Manim code generator for complex animations. Generate clean, working Python code.

⚠️ CRITICAL: LaTeX is NOT installed. You MUST NOT use MathTex() or Tex() at all.

MANDATORY RULES:
1. Output ONLY executable Python code (no markdown, no ```python blocks)
2. Always start with: from manim import *
3. Class must be named: GeneratedScene(Scene)
4. Use construct(self) method
5. For complex animations, break into clear sections with comments

FOR TEXT (REQUIRED):
- Use Text("message", font_size=X, color=Y) for ALL text
- Use Unicode symbols: ×, ÷, ², ³, √, π, ∑, ∫, ≈, ≤, ≥, ∞, α, β, γ, Δ, σ, Σ
- NEVER use MathTex() or Tex()

FOR COMPLEX SCENES:
- Use VGroup() to organize related objects
- Add clear comments for each major step
- Use self.wait() between major transitions
- Keep run_time reasonable (0.3-2 seconds per animation)

BEST PRACTICES:
- Define helper positions/constants at top
- Group related objects together
- Use meaningful variable names
- Add pauses for viewer comprehension
- Total animation under 30 seconds
"""

try:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": code_system},
            {"role": "user", "content": f"Create this complex animation:\n{enhanced_prompt}"},
        ],
        temperature=0.4,
        max_tokens=3500,
        timeout=90,
    )
    
    manim_code = response.choices[0].message.content.strip()
    
    # Clean code
    if "```python" in manim_code:
        manim_code = manim_code.split("```python")[1].split("```")[0].strip()
    elif "```" in manim_code:
        manim_code = manim_code.split("```")[1].split("```")[0].strip()
    
    print(f"✓ Generated code ({len(manim_code)} characters)")
    print(f"\nCODE PREVIEW (first 50 lines):")
    print("-" * 70)
    lines = manim_code.split("\n")
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3}. {line}")
    if len(lines) > 50:
        print(f"... ({len(lines) - 50} more lines)")
    print("-" * 70)
    
except Exception as e:
    print(f"✗ Code generation failed: {e}")
    exit(1)

# Step 3: Render animation
print("\n[3/3] Rendering super complex animation...")
print("⏱️  This may take 2-5 minutes for very complex scenes...")
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
            print(f"\n✓ Animation rendered successfully!")
            print(f"  - Execution time: {result.get('execution_time'):.2f}s")
            print(f"  - Video size: {len(result.get('video_data', '')) / 1024:.1f} KB")
            
            # Save video
            video_data = base64.b64decode(result["video_data"])
            output_file = f"test_super_complex_{selected['name'].replace(' ', '_').lower()}.mp4"
            with open(output_file, "wb") as f:
                f.write(video_data)
            print(f"  - Saved to: {output_file}")
            
            if result.get("warnings"):
                print("\n⚠️  Warnings:")
                for warning in result["warnings"]:
                    print(f"    {warning}")
                    
        else:
            print(f"\n✗ Rendering failed!")
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
    print("\n✗ Request timed out after 5 minutes")
    print("The animation is extremely complex. Consider simplifying.")
    exit(1)
except Exception as e:
    print(f"\n✗ Rendering request failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("✅ SUPER COMPLEX ANIMATION TEST PASSED!")
print("=" * 70)
print(f"\nYour complex animation is ready: {output_file}")
print("This demonstrates the system can handle very advanced visualizations!")
