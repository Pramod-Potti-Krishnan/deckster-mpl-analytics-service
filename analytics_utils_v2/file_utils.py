"""
File Utilities for Analytics V2
================================

Utilities for saving charts and data to files.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def save_chart_as_png(
    base64_image: str,
    output_path: str,
    filename: Optional[str] = None
) -> str:
    """
    Save base64 encoded image as PNG file.
    
    Args:
        base64_image: Base64 encoded image string
        output_path: Directory to save the file
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Full path to saved PNG file
    """
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{timestamp}.png"
    elif not filename.endswith('.png'):
        filename += '.png'
    
    # Full file path
    file_path = os.path.join(output_path, filename)
    
    try:
        # Decode base64 and save as PNG
        image_data = base64.b64decode(base64_image)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Chart saved as PNG: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save PNG: {e}")
        raise


def save_chart_data_as_json(
    data: Dict[str, Any],
    output_path: str,
    filename: Optional[str] = None
) -> str:
    """
    Save chart data as JSON file.
    
    Args:
        data: Chart data dictionary
        output_path: Directory to save the file
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Full path to saved JSON file
    """
    # Create output directory if it doesn't exist
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_data_{timestamp}.json"
    elif not filename.endswith('.json'):
        filename += '.json'
    
    # Full file path
    file_path = os.path.join(output_path, filename)
    
    try:
        # Save data as JSON
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Data saved as JSON: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        raise


def save_analytics_output(
    response: Dict[str, Any],
    output_dir: str = "analytics_output",
    base_filename: Optional[str] = None
) -> Dict[str, str]:
    """
    Save complete analytics output (PNG chart + JSON data).
    
    Args:
        response: Analytics API response
        output_dir: Directory for output files
        base_filename: Base name for files (without extension)
        
    Returns:
        Dictionary with paths to saved files
    """
    if not base_filename:
        # Generate from title or timestamp
        if response.get('metadata', {}).get('chart_type'):
            chart_type = response['metadata']['chart_type']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{chart_type}_{timestamp}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"analytics_{timestamp}"
    
    saved_files = {}
    
    # Save PNG if available
    if response.get('success') and response.get('chart'):
        try:
            png_path = save_chart_as_png(
                response['chart'],
                output_dir,
                f"{base_filename}.png"
            )
            saved_files['png'] = png_path
        except Exception as e:
            logger.error(f"Failed to save PNG: {e}")
    
    # Save data as JSON
    if response.get('data'):
        try:
            json_path = save_chart_data_as_json(
                response['data'],
                output_dir,
                f"{base_filename}_data.json"
            )
            saved_files['json'] = json_path
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
    
    # Save metadata
    if response.get('metadata'):
        try:
            metadata_path = save_chart_data_as_json(
                response['metadata'],
                output_dir,
                f"{base_filename}_metadata.json"
            )
            saved_files['metadata'] = metadata_path
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    # Save Python code if available
    if response.get('python_code'):
        try:
            code_path = os.path.join(output_dir, f"{base_filename}.py")
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with open(code_path, 'w') as f:
                f.write(response['python_code'])
            saved_files['code'] = code_path
            logger.info(f"Python code saved: {code_path}")
        except Exception as e:
            logger.error(f"Failed to save Python code: {e}")
    
    logger.info(f"Analytics output saved: {saved_files}")
    return saved_files


def create_output_package(
    response: Dict[str, Any],
    output_dir: str = "analytics_output",
    package_name: Optional[str] = None
) -> str:
    """
    Create a complete output package with all files.
    
    Args:
        response: Analytics API response
        output_dir: Base output directory
        package_name: Name for the package subdirectory
        
    Returns:
        Path to package directory
    """
    if not package_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_type = response.get('metadata', {}).get('chart_type', 'chart')
        package_name = f"{chart_type}_{timestamp}"
    
    # Create package directory
    package_dir = os.path.join(output_dir, package_name)
    Path(package_dir).mkdir(parents=True, exist_ok=True)
    
    # Save all components
    saved_files = save_analytics_output(response, package_dir, "chart")
    
    # Create summary file
    summary = {
        "generated_at": datetime.now().isoformat(),
        "chart_type": response.get('metadata', {}).get('chart_type'),
        "success": response.get('success'),
        "files": saved_files,
        "data_source": response.get('metadata', {}).get('data_source'),
        "theme_applied": response.get('metadata', {}).get('theme_applied'),
        "insights": response.get('metadata', {}).get('insights', [])
    }
    
    summary_path = os.path.join(package_dir, "summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    logger.info(f"Output package created: {package_dir}")
    return package_dir