import os
import sys
import tempfile
import subprocess
import base64
import time
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Create FastAPI app instance
app = FastAPI(
    title="Manim Animation Server",
    description="HTTP API server for generating Manim animations",
    version="1.0.0"
)

# Request model for HTTP endpoints
class ManimCodeRequest(BaseModel):
    """Request model for Manim code validation and generation."""
    manim_code: str

class ManimExecutor:
    """Handles Manim code execution and video generation."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "manim_mcp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def sanitize_manim_code(self, manim_code: str) -> str:
        """Remove LaTeX dependencies and replace with Text()."""
        replacements = {
            "Tex(": "Text(",
            "MathTex(": "Text(",
            "get_graph_label(": "get_text_label(",
        }

        for old, new in replacements.items():
            manim_code = manim_code.replace(old, new)

        if "get_text_label" in manim_code:
            helper = """
from manim import Text

def get_text_label(axes, graph, label="Label", x_val=None):
    txt = Text(label, font_size=28)
    txt.next_to(graph, UP)
    return txt
"""
            manim_code = helper + "\n" + manim_code

        return manim_code
    
    def execute_manim_code(self, manim_code: str) -> dict:
        """
        Execute Manim code and return the generated video.
        
        Args:
            manim_code: Python code containing Manim scene
            
        Returns:
            dict with success status, video_data (base64), and metadata
        """
        start_time = time.time()
        
        # Create temporary directory for this execution
        exec_dir = self.temp_dir / f"exec_{int(time.time() * 1000)}"
        exec_dir.mkdir(exist_ok=True)
        
        try:
            # Sanitize code to remove LaTeX dependencies
            safe_code = self.sanitize_manim_code(manim_code)
            
            # Write Manim code to file
            script_path = exec_dir / "scene.py"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(safe_code)
            
            # Execute Manim via Python module to avoid PATH issues
            # Manim will handle ffmpeg lookup internally
            cmd = [
                sys.executable,
                "-m",
                "manim",
                "-ql",  # Low quality for faster rendering
                "--media_dir",
                str(exec_dir / "media"),
                str(script_path),
                "GeneratedScene",  # The class name we expect
            ]

            result = subprocess.run(
                cmd,
                cwd=str(exec_dir),
                capture_output=True,
                text=True,
                timeout=300,  # Increased to 5 minutes for complex animations
            )
            
            if result.returncode != 0:
                # Parse stderr for more specific error message
                stderr = result.stderr
                error_msg = "Manim execution failed"
                
                if "LaTeX" in stderr or "latex" in stderr:
                    error_msg = "LaTeX error - install LaTeX or simplify mathematical expressions"
                elif "SyntaxError" in stderr:
                    error_msg = "Python syntax error in generated code"
                elif "ImportError" in stderr or "ModuleNotFoundError" in stderr:
                    error_msg = "Missing Python module"
                elif "NameError" in stderr:
                    error_msg = "Undefined variable or function in code"
                
                return {
                    "success": False,
                    "error": error_msg,
                    "stderr": stderr[-2000:],  # Last 2000 chars of stderr
                }
            
            # Find the generated video file
            video_path = self._find_video_file(exec_dir)
            
            if not video_path:
                return {
                    "success": False,
                    "error": "Video file not found after execution",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            # Read and encode video
            with open(video_path, 'rb') as video_file:
                video_data = base64.b64encode(video_file.read()).decode('utf-8')
            
            execution_time = time.time() - start_time
            
            # Clean up temporary files
            self._cleanup(exec_dir)
            
            return {
                "success": True,
                "video_data": video_data,
                "execution_time": execution_time,
                "video_size_bytes": len(video_data),
                "resolution": "480p",
                "latex": "disabled",
                "message": "Animation generated successfully"
            }
            
        except subprocess.TimeoutExpired:
            self._cleanup(exec_dir)
            return {
                "success": False,
                "error": "Animation timeout (>5 minutes). Try a simpler animation or reduce duration."
            }
        except Exception as e:
            self._cleanup(exec_dir)
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _find_video_file(self, exec_dir: Path) -> Optional[Path]:
        """Find the generated video file in the media directory."""
        media_dir = exec_dir / "media"
        
        if not media_dir.exists():
            return None
        
        # Search for mp4 files
        video_files = list(media_dir.rglob("*.mp4"))
        
        if video_files:
            # Return the most recently created video
            return max(video_files, key=lambda p: p.stat().st_mtime)
        
        return None
    
    def _cleanup(self, exec_dir: Path):
        """Clean up temporary execution directory."""
        try:
            import shutil
            if exec_dir.exists():
                shutil.rmtree(exec_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup {exec_dir}: {e}")


# Global executor instance
executor = ManimExecutor()


# HTTP Endpoints for FastAPI
@app.post("/generate_animation")
async def http_generate_animation(request: ManimCodeRequest):
    """
    HTTP endpoint to generate animation from Manim code.
    """
    try:
        result = executor.execute_manim_code(request.manim_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate_manim_code")
async def http_validate_manim_code(request: ManimCodeRequest):
    """
    HTTP endpoint to validate Manim code.
    """
    try:
        compile(request.manim_code, '<string>', 'exec')
        
        warnings = []
        # Flag LaTeX usage as error since it's not installed
        if "Tex(" in request.manim_code or "MathTex(" in request.manim_code:
            return {
                "valid": False, 
                "error": "LaTeX not installed. Use Text() with Unicode symbols instead of MathTex() or Tex(). Example: Text('E=mc²') instead of MathTex(r'E=mc^2')"
            }
        
        if 'class GeneratedScene' not in request.manim_code:
            return {
                "valid": False,
                "error": "Code must contain a class named 'GeneratedScene'"
            }
        
        if 'from manim import' not in request.manim_code:
            warnings.append("Code should import from manim")
        
        return {
            "valid": True,
            "warnings": warnings,
            "message": "Code syntax is valid"
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error: {str(e)}"
        }


@app.get("/status")
async def http_get_status():
    """
    HTTP endpoint to get server status.
    """
    import platform
    
    return {
        "status": "running",
        "server_name": "Manim Animation Server",
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "temp_directory": str(executor.temp_dir),
        "latex": "disabled",
        "available_endpoints": ["/generate_animation", "/validate_manim_code", "/status"]
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Manim Animation Server",
        "version": "1.0.0",
        "description": "MCP server for generating Manim animations via HTTP",
        "endpoints": {
            "POST /generate_animation": "Generate animation from Manim code",
            "POST /validate_manim_code": "Validate Manim code syntax",
            "GET /status": "Get server status",
            "GET /": "API information"
        }
    }


if __name__ == "__main__":
    # Run the FastAPI server with HTTP endpoints
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
