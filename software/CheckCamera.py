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

def check_libcamera():
    """Check if camera is detected using libcamera."""
    try:
        result = subprocess.run(
            ["libcamera-hello", "--list-cameras"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # If cameras are listed, then at least one camera is available
        return len(result.stdout.strip()) > 0 and "Available cameras" in result.stdout
    except Exception as e:
        print(f"Error checking camera with libcamera: {e}", file=sys.stderr)
        return False

def check_picamera():
    """Check if camera can be initialized with picamera2."""
    if not PICAMERA_AVAILABLE:
        return False
    
    try:
        # Try to initialize camera
        picam2 = Picamera2()
        
        # If we got here, camera is available
        camera_available = True
        camera_model = picam2.camera_properties.get('Model', 'Unknown')
        
        # Clean up
        picam2.close()
        
        print(f"Camera detected via picamera2: {camera_model}")
        return camera_available, camera_model
    except Exception as e:
        print(f"Error initializing camera with picamera2: {e}", file=sys.stderr)
        return False, None

def get_camera_info():
    """Get detailed camera information."""
    info = {
        "available": False,
        "model": None,
        "error": None
    }
    
    # Check with libcamera first for Pi 5 compatibility
    libcamera_available = check_libcamera()
    
    # Then check with picamera2 if available
    if PICAMERA_AVAILABLE:
        try:
            picam2 = Picamera2()
            info["available"] = True  # If we got here without exception, camera is available
            properties = picam2.camera_properties
            info["model"] = properties.get("Model", "Unknown Camera")
            picam2.close()
        except Exception as e:
            if libcamera_available:
                # Camera was detected with libcamera but not picamera2
                info["error"] = f"Camera detected but could not be initialized: {e}"
            else:
                info["error"] = f"Camera not detected: {e}"
                info["available"] = False
    else:
        if libcamera_available:
            info["available"] = True
            info["model"] = "Unknown Camera (detected via libcamera)"
        else:
            info["error"] = "Camera not detected and picamera2 module not available"
            info["available"] = False
    
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
