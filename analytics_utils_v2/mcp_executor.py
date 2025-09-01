"""
MCP Executor V2
===============

Simplified MCP executor for chart code execution.
Handles Python code execution via MCP or returns code for manual execution.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import logging
import base64
import re
from typing import Optional, Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)


class MCPExecutor:
    """
    Simplified MCP executor for chart generation.
    Two modes: Execute with MCP or return code.
    """
    
    def __init__(self, mcp_tool=None):
        """
        Initialize the executor.
        
        Args:
            mcp_tool: MCP execution function (e.g., mcp__ide__executeCode)
        """
        self.mcp_tool = mcp_tool
        self.is_available = mcp_tool is not None
        
        if self.is_available:
            logger.info("MCP executor initialized with tool")
        else:
            logger.info("MCP executor initialized without tool (code-only mode)")
    
    def set_mcp_tool(self, mcp_tool):
        """Update the MCP tool."""
        self.mcp_tool = mcp_tool
        self.is_available = mcp_tool is not None
        logger.info(f"MCP tool {'updated' if self.is_available else 'removed'}")
    
    async def execute_chart_code(self, python_code: str) -> Dict[str, Any]:
        """
        Execute chart code via MCP or return for manual execution.
        
        Args:
            python_code: Python code that generates a matplotlib chart
            
        Returns:
            Dictionary with execution result:
            - If MCP available: {"type": "image", "content": base64_str, "format": "base64"}
            - If MCP unavailable: {"type": "code", "content": python_code, "format": "python_code"}
        """
        if not self.is_available:
            logger.info("MCP not available, returning Python code")
            return {
                "type": "code",
                "content": python_code,
                "format": "python_code",
                "message": "MCP not available, returning Python code for manual execution"
            }
        
        try:
            # Wrap code for proper matplotlib handling
            wrapped_code = self._wrap_for_matplotlib(python_code)
            
            # Execute via MCP
            logger.debug("Executing code via MCP...")
            result = await self.mcp_tool(code=wrapped_code)
            
            # Extract base64 image
            base64_img = self._extract_base64(result)
            
            if base64_img:
                logger.info("Successfully generated chart via MCP")
                return {
                    "type": "image",
                    "content": base64_img,
                    "format": "base64"
                }
            else:
                logger.warning("MCP execution completed but no image generated")
                return {
                    "type": "code",
                    "content": python_code,
                    "format": "python_code",
                    "message": "Execution completed but no image was generated"
                }
                
        except Exception as e:
            logger.error(f"MCP execution failed: {e}")
            return {
                "type": "code",
                "content": python_code,
                "format": "python_code",
                "message": f"MCP execution failed: {str(e)}"
            }
    
    def _wrap_for_matplotlib(self, code: str) -> str:
        """
        Wrap code to ensure matplotlib outputs are captured.
        
        Args:
            code: Original Python code
            
        Returns:
            Wrapped code with proper imports and output handling
        """
        # Check if code already has necessary imports
        has_io_import = "from io import BytesIO" in code or "import io" in code
        has_base64_import = "import base64" in code
        has_plt_import = "import matplotlib.pyplot as plt" in code
        
        # Build wrapped code
        wrapped = ""
        
        # Add missing imports
        if not has_io_import:
            wrapped += "from io import BytesIO\n"
        if not has_base64_import:
            wrapped += "import base64\n"
        if not has_plt_import:
            wrapped += "import matplotlib.pyplot as plt\n"
        
        # Add matplotlib backend setting
        if "matplotlib.use" not in code:
            wrapped += "import matplotlib\nmatplotlib.use('Agg')\n"
        
        wrapped += "\n# Original code\n"
        wrapped += code
        
        # Add output capture if not present
        if "plt.savefig" not in code:
            wrapped += """
# Save figure to buffer
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
buffer.seek(0)

# Convert to base64
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
buffer.close()

# Display for MCP
print(f"IMAGE_BASE64:{image_base64}")
"""
        elif "base64" not in code:
            # Replace file save with buffer save
            wrapped = wrapped.replace(
                "plt.savefig('output.png'",
                """buffer = BytesIO()
plt.savefig(buffer, format='png'"""
            )
            wrapped += """
buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
buffer.close()
print(f"IMAGE_BASE64:{image_base64}")
"""
        
        return wrapped
    
    def _extract_base64(self, result: Any) -> Optional[str]:
        """
        Extract base64 image from MCP result.
        
        Args:
            result: Result from MCP execution
            
        Returns:
            Base64 string if found, None otherwise
        """
        if not result:
            return None
        
        # Handle different result formats
        if isinstance(result, dict):
            # Check for direct base64 in result
            if "image" in result:
                return result["image"]
            if "base64" in result:
                return result["base64"]
            if "output" in result:
                output = result["output"]
                if isinstance(output, str):
                    # Look for base64 in output
                    return self._extract_base64_from_string(output)
        
        elif isinstance(result, str):
            return self._extract_base64_from_string(result)
        
        # Try to extract from string representation
        try:
            result_str = str(result)
            return self._extract_base64_from_string(result_str)
        except:
            pass
        
        return None
    
    def _extract_base64_from_string(self, text: str) -> Optional[str]:
        """
        Extract base64 image from text output.
        
        Args:
            text: Text that might contain base64 image
            
        Returns:
            Base64 string if found
        """
        if not text:
            return None
        
        # Look for marked base64
        if "IMAGE_BASE64:" in text:
            match = re.search(r"IMAGE_BASE64:([A-Za-z0-9+/=]+)", text)
            if match:
                return match.group(1)
        
        # Look for data URL
        if "data:image/png;base64," in text:
            match = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", text)
            if match:
                return match.group(1)
        
        # Check if entire string looks like base64
        # Base64 images are typically very long
        if len(text) > 1000 and re.match(r"^[A-Za-z0-9+/=]+$", text.strip()):
            return text.strip()
        
        return None
    
    async def execute_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Execute a Python file and capture chart output.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Execution result dictionary
        """
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            return await self.execute_chart_code(code)
            
        except Exception as e:
            logger.error(f"Failed to execute file {file_path}: {e}")
            return {
                "type": "error",
                "content": None,
                "format": "error",
                "message": str(e)
            }
    
    def validate_code(self, python_code: str) -> Dict[str, Any]:
        """
        Validate Python code before execution.
        
        Args:
            python_code: Python code to validate
            
        Returns:
            Validation result with any warnings or errors
        """
        issues = []
        warnings = []
        
        # Check for required imports
        if "matplotlib" not in python_code and "plt" not in python_code:
            issues.append("No matplotlib import found")
        
        # Check for figure creation
        if "plt.subplots" not in python_code and "plt.figure" not in python_code:
            warnings.append("No explicit figure creation found")
        
        # Check for data
        if "=" not in python_code:
            issues.append("No data assignments found")
        
        # Check for plot commands
        plot_commands = ["plot", "bar", "scatter", "hist", "pie", "imshow"]
        if not any(cmd in python_code for cmd in plot_commands):
            issues.append("No plotting commands found")
        
        # Check for output
        if "plt.show" not in python_code and "plt.savefig" not in python_code:
            warnings.append("No output command (show/savefig) found")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def is_mcp_available(self) -> bool:
        """Check if MCP is available."""
        return self.is_available
    
    def get_execution_mode(self) -> str:
        """Get current execution mode."""
        return "mcp" if self.is_available else "code_only"