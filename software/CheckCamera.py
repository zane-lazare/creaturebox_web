#!/usr/bin/python

"""
CheckCamera - Simple script to check if camera is available and functioning
Designed to be used with Creaturebox Web Interface
"""

import sys
import json
import subprocess
import os
from pathlib import Path
import time

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False

def check_vcgencmd():
    """Check if camera is detected using vcgencmd."""
    try:
        result = subprocess.run(
            ["vcgencmd", "get_camera"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "detected=1" in result.stdout
    except Exception as e:
        print(f"Error checking camera with vcgencmd: {e}", file=sys.stderr)
        return False

def check_picamera():
    """Check if camera can be initialized with picamera2."""
    if not PICAMERA_AVAILABLE:
        return False
    
    try:
        # Try to initialize camera
        picam2 = Picamera2()
        # If no exception, camera is available
        print("Camera detected via picamera2")
        
        # Get camera info
        print(f"Camera model: {picam2.camera_properties.get('Model', 'Unknown')}")
        
        # Clean up
        picam2.close()
        return True
    except Exception as e:
        print(f"Error initializing camera with picamera2: {e}", file=sys.stderr)
        return False

def get_camera_info():
    """Get detailed camera information."""
    info = {
        "available": False,
        "model": None,
        "error": None
    }
    
    # First check with vcgencmd
    if check_vcgencmd():
        info["available"] = True
    
    # Then check with picamera2 if available
    if PICAMERA_AVAILABLE:
        try:
            picam2 = Picamera2()
            properties = picam2.camera_properties
            info["model"] = properties.get("Model", "Unknown Camera")
            picam2.close()
        except Exception as e:
            if info["available"]:
                # Camera was detected with vcgencmd but not picamera2
                info["error"] = f"Camera detected but could not be initialized: {e}"
            else:
                info["error"] = f"Camera not detected: {e}"
    else:
        if info["available"]:
            info["error"] = "Camera detected but picamera2 module not available"
        else:
            info["error"] = "Camera not detected and picamera2 module not available"
    
    return info

if __name__ == "__main__":
    try:
        info = get_camera_info()
        # Output as JSON for easy parsing
        print(json.dumps(info))
    except Exception as e:
        print(json.dumps({
            "available": False,
            "model": None,
            "error": f"Error checking camera: {str(e)}"
        }))
