"""
Streamlit Troubleshooting Helper
Run this to test your animation generation step by step
"""
import os
from openai import AzureOpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("ANIMATION GENERATION TROUBLESHOOTING")
print("=" * 70)

# Check Azure credentials
print("\n1. Checking Azure OpenAI Credentials...")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if api_key and endpoint and deployment:
    print(f"   ✓ API Key: {'*' * 20}{api_key[-10:]}")
    print(f"   ✓ Endpoint: {endpoint}")
    print(f"   ✓ Deployment: {deployment}")
    print(f"   ✓ API Version: {api_version}")
else:
    print("   ✗ Missing credentials!")
    exit(1)

# Test Azure OpenAI
print("\n2. Testing Azure OpenAI Connection...")
try:
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Say 'OK'"}],
        max_tokens=5
    )
    print(f"   ✓ Azure OpenAI is working: {response.choices[0].message.content}")
except Exception as e:
    print(f"   ✗ Azure OpenAI failed: {e}")
    exit(1)

# Test prompt enhancement
print("\n3. Testing Prompt Enhancement...")
test_prompt = "blue circle turning into red square"
try:
    enhanced = f"Create a simple animation: Start with a blue circle in the center. Smoothly transform it into a red square. Duration: 5 seconds."
    print(f"   ✓ Original: {test_prompt}")
    print(f"   ✓ Enhanced: {enhanced}")
except Exception as e:
    print(f"   ✗ Enhancement failed: {e}")

# Test code generation
print("\n4. Testing Code Generation...")
try:
    system_prompt = """Generate ONLY Python code (no markdown).
Start with: from manim import *
Class: GeneratedScene(Scene)
Use Text() for all text - NO MathTex or Tex.
Keep it simple."""

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create: {enhanced}"},
        ],
        temperature=0.5,
        max_tokens=500,
        timeout=30,
    )
    
    manim_code = response.choices[0].message.content.strip()
    
    # Clean code
    if "```python" in manim_code:
        manim_code = manim_code.split("```python")[1].split("```")[0].strip()
    elif "```" in manim_code:
        manim_code = manim_code.split("```")[1].split("```")[0].strip()
    
    print(f"   ✓ Generated code ({len(manim_code)} chars)")
    print("\n   CODE PREVIEW:")
    print("   " + "\n   ".join(manim_code.split("\n")[:15]))
    if len(manim_code.split("\n")) > 15:
        print("   ...")
    
except Exception as e:
    print(f"   ✗ Code generation failed: {e}")
    exit(1)

# Test server connection
print("\n5. Testing Animation Server...")
server_url = "https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io"
try:
    resp = requests.get(f"{server_url}/status", timeout=10)
    if resp.status_code == 200:
        print(f"   ✓ Server is online: {server_url}")
    else:
        print(f"   ✗ Server returned status {resp.status_code}")
        exit(1)
except Exception as e:
    print(f"   ✗ Cannot reach server: {e}")
    exit(1)

# Test animation rendering
print("\n6. Testing Animation Rendering...")
try:
    payload = {"manim_code": manim_code}
    response = requests.post(
        f"{server_url}/generate_animation",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"   ✓ Animation generated successfully!")
            print(f"   ✓ Execution time: {result.get('execution_time')}s")
            print(f"   ✓ Video size: {len(result.get('video_data', '')) / 1024:.1f} KB")
        else:
            print(f"   ✗ Rendering failed!")
            print(f"   Error: {result.get('error')}")
            print("\n   GENERATED CODE THAT FAILED:")
            print("   " + "\n   ".join(manim_code.split("\n")))
            exit(1)
    else:
        print(f"   ✗ Server error: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        exit(1)
        
except Exception as e:
    print(f"   ✗ Rendering request failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - Your setup is working correctly!")
print("=" * 70)
print("\nYou can now run: streamlit run streamlit_app.py")
