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

def get_camera_info():
    """Get detailed camera information."""
    info = {
        "available": False,
        "model": None,
        "error": None
    }
    
    # Check with picamera2 if available
    if PICAMERA_AVAILABLE:
        try:
            # Try to initialize camera
            picam2 = Picamera2()
            
            # If we got this far without an exception, the camera is available
            info["available"] = True
            
            # Get model information
            properties = picam2.camera_properties
            info["model"] = properties.get("Model", "Unknown Camera")
            
            # Debug output to stderr
            print(f"Camera detected successfully: {info['model']}", file=sys.stderr)
            
            # Clean up
            picam2.close()
        except Exception as e:
            info["error"] = f"Error initializing camera: {str(e)}"
            print(f"Error initializing camera: {e}", file=sys.stderr)
    else:
        info["error"] = "Picamera2 module not available"
        print("Picamera2 module not available", file=sys.stderr)
    
    return info

if __name__ == "__main__":
    try:
        info = get_camera_info()
        
        # Force available to True if we have a camera model
        if info["model"] and not info["available"]:
            print(f"Camera model detected ({info['model']}), forcing available=True", file=sys.stderr)
            info["available"] = True
        
        # Output as JSON for easy parsing
        print(json.dumps(info))
    except Exception as e:
        print(json.dumps({
            "available": False,
            "model": None,
            "error": f"Error checking camera: {str(e)}"
        }))
