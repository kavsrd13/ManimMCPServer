"""
Test script to verify LaTeX capabilities in deployed Manim server
"""
import requests
import json
import base64

SERVER_URL = "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"

# Test 1: Validate LaTeX code
print("=" * 60)
print("Test 1: Validating Manim code with LaTeX (MathTex)")
print("=" * 60)

latex_code = """
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Display Einstein's famous equation using LaTeX
        equation = MathTex(r"E = mc^2")
        equation.scale(2)
        
        # Animate the equation
        self.play(Write(equation))
        self.wait(1)
        
        # Transform to expanded form
        expanded = MathTex(r"E = ", r"m", r"c", r"^2")
        expanded.scale(2)
        self.play(TransformMatchingTex(equation, expanded))
        self.wait(1)
"""

validate_response = requests.post(
    f"{SERVER_URL}/validate_manim_code",
    json={"manim_code": latex_code}
)

print(f"Status: {validate_response.status_code}")
print(f"Response: {json.dumps(validate_response.json(), indent=2)}")
print()

# Test 2: Generate LaTeX animation
print("=" * 60)
print("Test 2: Generating animation with LaTeX")
print("=" * 60)

if validate_response.json().get("valid"):
    generate_response = requests.post(
        f"{SERVER_URL}/generate_animation",
        json={"manim_code": latex_code}
    )
    
    result = generate_response.json()
    print(f"Status: {generate_response.status_code}")
    print(f"Success: {result.get('success')}")
    print(f"LaTeX: {result.get('latex')}")
    print(f"Message: {result.get('message')}")
    
    if result.get('success'):
        print(f"Execution time: {result.get('execution_time'):.2f}s")
        print(f"Video size: {result.get('video_size_bytes')} bytes")
        
        # Save the video
        if 'video_data' in result:
            video_bytes = base64.b64decode(result['video_data'])
            output_path = "latex_test_animation.mp4"
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
            print(f"✅ Video saved to: {output_path}")
    else:
        print(f"❌ Error: {result.get('error')}")
        if 'stderr' in result:
            print(f"Stderr: {result['stderr'][-500:]}")
else:
    print("❌ Validation failed, skipping generation")

print()
print("=" * 60)
print("LaTeX Support Test Complete!")
print("=" * 60)
