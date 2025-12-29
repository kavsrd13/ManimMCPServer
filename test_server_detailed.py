import requests
import json

url = 'https://manim-mcp-app.salmonforest-f54e4566.eastus.azurecontainerapps.io/generate_animation'

# Simple test code
code = '''from manim import *

class GeneratedScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.wait(1)
'''

print("Testing Azure server with simple animation...")
print("=" * 60)

try:
    response = requests.post(url, json={'manim_code': code}, timeout=120)
    print(f"Status Code: {response.status_code}")
    print()
    
    result = response.json()
    print(f"Success: {result.get('success')}")
    print()
    
    if not result.get('success'):
        print("ERROR DETAILS:")
        print(result.get('error', 'No error message'))
        print()
    
    print("FULL RESPONSE:")
    print(json.dumps(result, indent=2)[:1000])
    
except Exception as e:
    print(f"Request failed: {e}")
