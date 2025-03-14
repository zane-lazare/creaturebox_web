#!/usr/bin/env python3
"""
Update TakePhoto.py Script

This script updates the TakePhoto.py script to use the correct paths.
"""

import os
import sys
import re
import shutil

# Configuration paths
CONFIG_DIR = "/home/creature/.config/creaturebox"
PHOTOS_DIR = "/home/creature/creaturebox_photos"

def update_takephoto_script(script_path):
    """
    Update the TakePhoto.py script to use the correct paths.
    
    Args:
        script_path: Path to the TakePhoto.py script
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(script_path):
        print(f"Error: Script not found at {script_path}")
        return False
    
    # Make a backup
    backup_path = f"{script_path}.bak"
    try:
        shutil.copy2(script_path, backup_path)
        print(f"Created backup: {backup_path}")
    except Exception as e:
        print(f"Warning: Failed to create backup: {e}")
    
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Update desktop_path
        content = re.sub(
            r'desktop_path\s*=\s*Path\s*\(\s*"[^"]*"\s*\)',
            f'desktop_path = Path("{CONFIG_DIR}")',
            content
        )
        
        # Update controls_path
        content = re.sub(
            r'control_values_fpath\s*=\s*"[^"]*"',
            f'control_values_fpath = "{CONFIG_DIR}/controls.txt"',
            content
        )
        
        # Update default_path for camera settings
        content = re.sub(
            r'default_path\s*=\s*"[^"]*"',
            f'default_path = "{CONFIG_DIR}/camera_settings.csv"',
            content
        )
        
        # Update photos path
        content = re.sub(
            r'folderPath\s*=\s*"[^"]*"',
            f'folderPath = "{PHOTOS_DIR}/"',
            content
        )
        
        with open(script_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {script_path} with correct paths.")
        return True
        
    except Exception as e:
        print(f"Error updating script: {e}")
        
        # Try to restore backup if something went wrong
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, script_path)
                print(f"Restored backup due to error.")
        except Exception as restore_error:
            print(f"Warning: Failed to restore backup: {restore_error}")
            
        return False

def main():
    # If path is provided as argument, use it, otherwise use default
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
    else:
        # Try to find the script in common locations
        potential_paths = [
            # Installation path
            "/opt/creaturebox_web/software/TakePhoto.py",
            # Repository paths
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "software", "TakePhoto.py")
        ]
        
        script_path = None
        for path in potential_paths:
            if os.path.exists(path):
                script_path = path
                break
        
        if not script_path:
            print("Error: Could not find TakePhoto.py script. Please provide path as argument.")
            return 1
    
    success = update_takephoto_script(script_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
