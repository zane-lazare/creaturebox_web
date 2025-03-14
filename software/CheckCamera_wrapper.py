#!/usr/bin/env python3
"""
Wrapper for CheckCamera.py to provide JSON formatted output.
This script executes the original CheckCamera.py and formats its output as JSON.
"""

import subprocess
import sys
import json
import os
import re
import time

def run_checkcamera():
    # Get the path to the original CheckCamera.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "CheckCamera.py")
    
    start_time = time.time()
    
    # Pass any arguments to the original script
    args = [sys.executable, script_path] + sys.argv[1:]
    
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        
        # Try to detect camera status from output
        camera_detected = False
        camera_model = None
        error_message = None
        
        # Look for camera detection phrases
        if "Camera detected" in result.stdout:
            camera_detected = True
            
        # Try to extract camera model if mentioned
        model_match = re.search(r"Model:\s*(.+)", result.stdout)
        if model_match:
            camera_model = model_match.group(1).strip()
            
        # Look for any error messages
        error_match = re.search(r"Error:(.+)", result.stdout)
        if error_match:
            error_message = error_match.group(1).strip()
        
        if result.stderr:
            error_message = result.stderr
        
        # Create structured JSON output
        output = {
            "available": camera_detected and result.returncode == 0,
            "model": camera_model,
            "error": error_message,
            "raw_output": result.stdout,
            "execution_time": time.time() - start_time
        }
        
        print(json.dumps(output))
        return 0 if output["available"] else 1
    except Exception as e:
        error_output = {
            "available": False,
            "model": None,
            "error": str(e),
            "raw_output": "",
            "execution_time": time.time() - start_time
        }
        print(json.dumps(error_output))
        return 1

if __name__ == "__main__":
    sys.exit(run_checkcamera())
