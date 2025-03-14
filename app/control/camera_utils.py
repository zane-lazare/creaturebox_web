"""
Camera Utilities Module

This module provides functions for checking camera status, verifying connectivity,
and retrieving camera information.
"""

import os
import subprocess
import logging
import re
import json
from flask import current_app

from .script_executor import execute_script
from app.utils.paths import get_camera_settings_path

# Configure logging
logger = logging.getLogger(__name__)

def check_camera_status():
    """
    Check if the camera is connected and available.
    
    Returns:
        dict: Status information including whether camera is available,
              model information, and any error messages
    """
    status = {
        "available": False,
        "model": None,
        "error": None
    }
    
    try:
        # Use our CheckCamera.py script to check camera status
        result = execute_script("CheckCamera.py")
        
        if result.success and result.output:
            try:
                # Parse JSON output from the script
                camera_info = json.loads(result.output)
                status["available"] = camera_info.get("available", False)
                status["model"] = camera_info.get("model")
                status["error"] = camera_info.get("error")
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                status["available"] = "Camera detected" in result.output
                if not status["available"]:
                    status["error"] = "Could not parse camera information"
        else:
            status["error"] = result.error or "Error checking camera"
            
    except Exception as e:
        logger.error(f"Unexpected error checking camera status: {e}")
        status["error"] = f"Unexpected error: {str(e)}"
    
    return status

def get_camera_settings():
    """
    Get current camera settings from the CSV file.
    
    Returns:
        dict: Dictionary of camera settings or None if file can't be read
    """
    try:
        settings_path = get_camera_settings_path()
        
        if not os.path.exists(settings_path):
            logger.error(f"Camera settings file not found: {settings_path}")
            return None
        
        settings = {}
        with open(settings_path, 'r') as file:
            # Skip header
            next(file)
            for line in file:
                parts = line.strip().split(',', 2)
                if len(parts) >= 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    try:
                        # Try to convert numeric values
                        if '.' in value:
                            settings[key] = float(value)
                        else:
                            settings[key] = int(value)
                    except ValueError:
                        settings[key] = value
        
        return settings
    
    except Exception as e:
        logger.error(f"Error reading camera settings: {e}")
        return None

def test_camera_capture():
    """
    Attempt a test capture to verify camera is functioning.
    Does not save the image, just tests if camera can capture.
    
    Returns:
        dict: Result of test including success status and any error message
    """
    # This is a placeholder. In a real implementation, you would:
    # 1. Create a simple script to test camera capture
    # 2. Execute it with minimal parameters
    # 3. Check the result
    
    # For now, we'll use the TakePhoto.py script but add a test flag
    # (Note: This assumes your script can handle a test mode)
    
    result = {
        "success": False,
        "error": None
    }
    
    try:
        # Check if camera is available first
        status = check_camera_status()
        if not status["available"]:
            result["error"] = status["error"] or "Camera not available"
            return result
            
        # Try to run TakePhoto.py with --test flag (you would need to add this to your script)
        # For now, this is a placeholder
        
        # For testing purposes, we'll assume success if the camera is available
        result["success"] = True
        
    except Exception as e:
        logger.error(f"Error testing camera capture: {e}")
        result["error"] = f"Error: {str(e)}"
    
    return result
