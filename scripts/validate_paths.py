#!/usr/bin/env python3
"""
Path Validation Script for Creaturebox Web Interface

This script validates all paths used by the application and helps diagnose
path-related issues. It can also attempt to fix common path problems.
"""

import os
import sys
import argparse
import logging
import shutil

# Add the parent directory to the path so we can import our app modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# Try to import our path utilities
try:
    from app.utils.paths import (
        get_app_root, 
        get_config_dir, 
        get_photos_dir,
        get_script_path,
        validate_paths
    )
except ImportError:
    print("ERROR: Could not import path utilities. Make sure you're running this from the repository root.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('path_validator')

def check_wrapper_scripts():
    """Check if wrapper scripts exist and are executable."""
    app_root = get_app_root()
    issues = []
    fixes = []
    
    wrapper_scripts = [
        "TakePhoto_wrapper.py",
        "CheckCamera_wrapper.py"
    ]
    
    for script in wrapper_scripts:
        # Check if wrapper script exists
        script_path = get_script_path(script)
        if not script_path or not os.path.exists(script_path):
            # Look for original script to create wrapper
            orig_script = script.replace("_wrapper", "")
            orig_path = get_script_path(orig_script)
            
            if orig_path and os.path.exists(orig_path):
                # Wrapper is missing but we can create it
                issues.append(f"Wrapper script {script} not found, but original {orig_script} exists.")
                # Add function to create wrapper script
                fixes.append(("create_wrapper", orig_script, os.path.dirname(orig_path)))
            else:
                # Both original and wrapper are missing
                issues.append(f"Neither {script} nor {orig_script} found.")
                fixes.append(None)  # No automatic fix available
        elif not os.access(script_path, os.X_OK):
            # Wrapper exists but isn't executable
            issues.append(f"Wrapper script {script} exists but is not executable.")
            fixes.append(("make_executable", script_path))
    
    return issues, fixes

def create_wrapper_script(original_script, directory):
    """
    Create a wrapper script for the given original script.
    
    Args:
        original_script: Name of the original script (e.g., TakePhoto.py)
        directory: Directory where the original script is located
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        wrapper_name = original_script.replace(".py", "_wrapper.py")
        wrapper_path = os.path.join(directory, wrapper_name)
        
        if "Camera" in original_script:
            # Create CheckCamera wrapper
            wrapper_content = """#!/usr/bin/env python3
\"\"\"
Wrapper for {original} to provide JSON formatted output.
This script executes the original {original} and formats its output as JSON.
\"\"\"

import subprocess
import sys
import json
import os
import re
import time

def run_checkcamera():
    # Get the path to the original script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "{original}")
    
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
        model_match = re.search(r"Model:\\s*(.+)", result.stdout)
        if model_match:
            camera_model = model_match.group(1).strip()
            
        # Look for any error messages
        error_match = re.search(r"Error:(.+)", result.stdout)
        if error_match:
            error_message = error_match.group(1).strip()
        
        if result.stderr:
            error_message = result.stderr
        
        # Create structured JSON output
        output = {{
            "available": camera_detected and result.returncode == 0,
            "model": camera_model,
            "error": error_message,
            "raw_output": result.stdout,
            "execution_time": time.time() - start_time
        }}
        
        print(json.dumps(output))
        return 0 if output["available"] else 1
    except Exception as e:
        error_output = {{
            "available": False,
            "model": None,
            "error": str(e),
            "raw_output": "",
            "execution_time": time.time() - start_time
        }}
        print(json.dumps(error_output))
        return 1

if __name__ == "__main__":
    sys.exit(run_checkcamera())
""".format(original=original_script)
        else:
            # Create TakePhoto wrapper
            wrapper_content = """#!/usr/bin/env python3
\"\"\"
Wrapper for {original} to provide JSON formatted output.
This script executes the original {original} and formats its output as JSON.
\"\"\"

import subprocess
import sys
import json
import os
import re
import time

def run_takephoto():
    # Get the path to the original script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "{original}")
    
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
        output = {{
            "success": result.returncode == 0 and not errors,
            "output": result.stdout,
            "error": "; ".join(errors) if errors else None,
            "image_path": saved_image_path,
            "execution_time": time.time() - start_time
        }}
        
        print(json.dumps(output))
        return 0 if output["success"] else 1
    except Exception as e:
        error_output = {{
            "success": False,
            "output": "",
            "error": str(e),
            "image_path": None,
            "execution_time": time.time() - start_time
        }}
        print(json.dumps(error_output))
        return 1

if __name__ == "__main__":
    sys.exit(run_takephoto())
""".format(original=original_script)
        
        # Write the wrapper script
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        # Make it executable
        os.chmod(wrapper_path, 0o755)
        
        logger.info(f"Created wrapper script {wrapper_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to create wrapper script: {e}")
        return False

def make_executable(path):
    """Make a file executable."""
    try:
        os.chmod(path, 0o755)
        logger.info(f"Made {path} executable")
        return True
    except Exception as e:
        logger.error(f"Failed to make {path} executable: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate and fix paths for Creaturebox Web Interface')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--fix', '-f', action='store_true', help='Attempt to fix path issues')
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate paths using the utils module
    logger.info("Validating paths...")
    results = validate_paths()
    
    # Check for required directories
    required_dirs = [
        get_app_root(),
        get_config_dir(),
        get_photos_dir()
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            if args.fix:
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    logger.error(f"Failed to create directory {directory}: {e}")
            else:
                logger.warning(f"Required directory does not exist: {directory}")
    
    # Check wrapper scripts
    logger.info("Checking wrapper scripts...")
    wrapper_issues, wrapper_fixes = check_wrapper_scripts()
    
    # Report issues
    if not results['success'] or wrapper_issues:
        logger.error("Path validation found issues:")
        for issue in results['issues']:
            logger.error(f"- {issue}")
        
        for issue in wrapper_issues:
            logger.error(f"- {issue}")
        
        # Try to fix issues if requested
        if args.fix:
            logger.info("Attempting to fix issues...")
            
            # Fix wrapper script issues
            for i, fix in enumerate(wrapper_fixes):
                if fix:
                    fix_type = fix[0]
                    if fix_type == "create_wrapper":
                        orig_script, orig_dir = fix[1], fix[2]
                        logger.info(f"Creating wrapper for {orig_script}...")
                        if create_wrapper_script(orig_script, orig_dir):
                            logger.info(f"Successfully created wrapper for {orig_script}")
                        else:
                            logger.error(f"Failed to create wrapper for {orig_script}")
                    
                    elif fix_type == "make_executable":
                        script_path = fix[1]
                        logger.info(f"Making {script_path} executable...")
                        if make_executable(script_path):
                            logger.info(f"Successfully made {script_path} executable")
                        else:
                            logger.error(f"Failed to make {script_path} executable")
            
            # Validate paths again after fixes
            logger.info("Re-validating paths after fixes...")
            new_results = validate_paths()
            if new_results['success']:
                logger.info("All path issues resolved successfully!")
            else:
                logger.warning("Some path issues could not be resolved:")
                for issue in new_results['issues']:
                    logger.warning(f"- {issue}")
    else:
        logger.info("Path validation successful - no issues found.")
    
    return 0 if results['success'] and not wrapper_issues else 1

if __name__ == '__main__':
    sys.exit(main())
