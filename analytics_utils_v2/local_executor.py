"""
Local Executor for Chart Generation
====================================

Fallback executor that runs Python code locally to generate charts.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import subprocess
import tempfile
import os
import base64
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LocalExecutor:
    """Execute Python chart code locally to generate PNG."""
    
    @staticmethod
    async def execute_chart_code(python_code: str) -> Dict[str, Any]:
        """
        Execute Python code locally and capture the generated chart.
        
        Args:
            python_code: Python code that generates a matplotlib chart
            
        Returns:
            Dictionary with execution result
        """
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write Python code to file
                code_file = os.path.join(tmpdir, "chart_code.py")
                output_file = os.path.join(tmpdir, "output.png")
                
                # Add matplotlib backend setting and modify code to save to specific location
                # Ensure matplotlib uses non-interactive backend
                backend_code = "import matplotlib\nmatplotlib.use('Agg')\n"
                
                # Add backend if not already present
                if "matplotlib.use" not in python_code:
                    if "import matplotlib" in python_code:
                        python_code = python_code.replace(
                            "import matplotlib.pyplot",
                            "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot"
                        )
                    else:
                        python_code = backend_code + python_code
                
                modified_code = python_code.replace(
                    "plt.savefig('output.png'",
                    f"plt.savefig('{output_file}'"
                )
                
                # Ensure the code saves the figure
                if "plt.savefig" not in modified_code:
                    modified_code = modified_code.replace(
                        "plt.show()",
                        f"plt.savefig('{output_file}', dpi=100, bbox_inches='tight')\nplt.show()"
                    )
                
                # Write code to file
                with open(code_file, 'w') as f:
                    f.write(modified_code)
                
                # Execute the code using python3
                python_executable = "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
                
                # Try multiple Python executables in order
                python_options = [
                    python_executable,
                    "python3",
                    "/usr/bin/python3",
                    "/usr/local/bin/python3"
                ]
                
                result = None
                for python_cmd in python_options:
                    try:
                        result = subprocess.run(
                            [python_cmd, code_file],
                            capture_output=True,
                            text=True,
                            timeout=30,
                            cwd=tmpdir
                        )
                        logger.info(f"Successfully executed with: {python_cmd}")
                        break
                    except FileNotFoundError:
                        logger.debug(f"Python not found at: {python_cmd}")
                        continue
                
                if result is None:
                    raise FileNotFoundError("No Python executable found")
                
                # Check if PNG was created
                if os.path.exists(output_file):
                    # Read and encode as base64
                    with open(output_file, 'rb') as f:
                        image_data = f.read()
                    
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    
                    logger.info("Successfully generated chart locally")
                    return {
                        "type": "image",
                        "content": base64_image,
                        "format": "base64"
                    }
                else:
                    logger.error(f"Chart generation failed: {result.stderr}")
                    return {
                        "type": "error",
                        "content": None,
                        "format": "error",
                        "message": f"No output generated: {result.stderr[:200]}"
                    }
                    
        except subprocess.TimeoutExpired:
            logger.error("Chart generation timed out")
            return {
                "type": "error",
                "content": None,
                "format": "error",
                "message": "Execution timed out"
            }
        except Exception as e:
            logger.error(f"Local execution failed: {e}")
            return {
                "type": "error",
                "content": None,
                "format": "error",
                "message": str(e)
            }