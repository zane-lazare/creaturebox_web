#!/usr/bin/env python3
"""
Wrapper for TakePhoto.py to provide JSON formatted output.
This script executes the original TakePhoto.py and formats its output as JSON.
"""

import subprocess
import sys
import json
import os
import re
import time

def run_takephoto():
    # Get the path to the original TakePhoto.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "TakePhoto.py")
    
    start_time = time.time()
    
    # Pass any arguments to the original script
    args = [sys.executable, script_path] + sys.argv[1:]
    
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        
        # Check for successful photo capture
        saved_image_path = None
        for line in result.stdout.splitlines():
            if "Image saved to" in line:
                saved_image_path = line.replace("Image saved to", "").strip()
        
        # Look for any error patterns
        errors = []
        error_patterns = [
            r"not enough space to take more photos",
            r"Error:",
            r"error:",
            r"failed"
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, result.stdout, re.IGNORECASE)
            if matches:
                errors.extend(matches)
        
        if result.stderr:
            errors.append(result.stderr)
        
        # Create a more structured output
        output = {
            "success": result.returncode == 0 and not errors,
            "output": result.stdout,
            "error": "; ".join(errors) if errors else None,
            "image_path": saved_image_path,
            "execution_time": time.time() - start_time
        }
        
        print(json.dumps(output))
        return 0 if output["success"] else 1
    except Exception as e:
        error_output = {
            "success": False,
            "output": "",
            "error": str(e),
            "image_path": None,
            "execution_time": time.time() - start_time
        }
        print(json.dumps(error_output))
        return 1

if __name__ == "__main__":
    sys.exit(run_takephoto())
