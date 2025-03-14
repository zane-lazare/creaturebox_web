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

# Debug mode
DEBUG = True

def debug(message):
    """Print debug message to stderr if DEBUG is True."""
    if DEBUG:
        print(f"DEBUG: {message}", file=sys.stderr)

debug("Script started")

try:
    debug("Importing Picamera2...")
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
    debug("Picamera2 imported successfully")
except ImportError as e:
    debug(f"Failed to import Picamera2: {e}")
    PICAMERA_AVAILABLE = False

def get_camera_info():
    """Get detailed camera information."""
    debug("Starting get_camera_info()")
    
    info = {
        "available": False,
        "model": None,
        "error": None
    }
    
    # Check with picamera2 if available
    if PICAMERA_AVAILABLE:
        debug("Picamera2 is available, trying to initialize camera")
        try:
            # Try to initialize camera
            debug("Creating Picamera2 instance...")
            picam2 = Picamera2()
            debug("Picamera2 instance created successfully")
            
            # If we got this far without an exception, the camera is available
            debug("Camera successfully initialized, setting available=True")
            info["available"] = True
            
            # Get model information
            debug("Getting camera properties...")
            properties = picam2.camera_properties
            model = properties.get("Model", "Unknown Camera")
            debug(f"Camera model: {model}")
            info["model"] = model
            
            # Clean up
            debug("Closing camera...")
            picam2.close()
            debug("Camera closed")
            
        except Exception as e:
            error_msg = f"Error initializing camera: {str(e)}"
            debug(f"Exception caught: {error_msg}")
            info["error"] = error_msg
    else:
        error_msg = "Picamera2 module not available"
        debug(error_msg)
        info["error"] = error_msg
    
    # Special case: If we have a model but available is somehow still False
    if info["model"] and not info["available"]:
        debug(f"INCONSISTENCY DETECTED: Model '{info['model']}' was found but available is False. Forcing available=True")
        info["available"] = True
    
    debug(f"Final info object: {info}")
    return info

def manual_camera_check():
    """Manual camera check as fallback."""
    debug("Performing manual camera check...")
    
    # Just check if camera device exists
    devices = ["/dev/video0", "/dev/media0", "/dev/media2"]
    for device in devices:
        if os.path.exists(device):
            debug(f"Found camera device: {device}")
            return True
    
    debug("No camera devices found")
    return False

if __name__ == "__main__":
    debug("Main execution started")
    try:
        # Get camera info
        info = get_camera_info()
        
        # Final fallback - if camera still not detected, check manually
        if not info["available"] and not info["error"]:
            debug("Camera not detected by Picamera2, trying manual fallback check")
            if manual_camera_check():
                debug("Manual check found camera, setting available=True")
                info["available"] = True
                if not info["model"]:
                    info["model"] = "Unknown Camera (detected via device check)"
        
        # Output as JSON for easy parsing
        debug("Outputting final JSON")
        debug(json.dumps(info))
        print(json.dumps(info))
        
    except Exception as e:
        error_msg = f"Error checking camera: {str(e)}"
        debug(f"Exception in main: {error_msg}")
        print(json.dumps({
            "available": False,
            "model": None,
            "error": error_msg
        }))
    
    debug("Script completed")
