"""
Test file for local development and testing of Manim animation generation.
"""

# Example Manim code that can be used for testing
EXAMPLE_MANIM_CODE = """
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Create a circle
        circle = Circle(radius=1, color=BLUE)
        
        # Create a square
        square = Square(side_length=2, color=GREEN)
        
        # Display the circle
        self.play(Create(circle))
        self.wait(0.5)
        
        # Transform circle into square
        self.play(Transform(circle, square))
        self.wait(0.5)
        
        # Rotate the square
        self.play(Rotate(circle, angle=PI))
        self.wait(1)
"""

# Example test for the MCP server
def test_generate_animation():
    """Test the generate_animation function locally."""
    from mcp_server import executor
    
    result = executor.execute_manim_code(EXAMPLE_MANIM_CODE)
    
    print("Test Results:")
    print(f"Success: {result.get('success')}")
    print(f"Execution Time: {result.get('execution_time', 0):.2f}s")
    
    if result.get('success'):
        print(f"Video Size: {result.get('video_size_bytes', 0)} bytes")
        print("✅ Animation generated successfully!")
    else:
        print(f"❌ Error: {result.get('error')}")
        if 'stderr' in result:
            print(f"Stderr: {result['stderr']}")

if __name__ == "__main__":
    test_generate_animation()
