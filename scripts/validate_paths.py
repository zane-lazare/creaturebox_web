#!/usr/bin/env python3
"""
Path Validation Script for Creaturebox Web

This script validates that all required paths exist and are accessible.
It can be run during installation or as a standalone script.
"""

import os
import sys
import json
import argparse

# Add parent directory to path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

def validate_paths(verbose=False, fix=False):
    """
    Validate that all required paths exist and are accessible.
    
    Args:
        verbose: Whether to print detailed information
        fix: Whether to attempt to fix issues
        
    Returns:
        dict: Validation results with issues found
    """
    try:
        from app.utils.paths import validate_paths, ensure_directory_exists
        from app.utils.paths import (
            CONFIG_DIR, PHOTOS_DIR, CAMERA_SETTINGS, CONTROLS_FILE, SCHEDULE_SETTINGS,
            DEFAULT_CAMERA_SETTINGS, DEFAULT_CONTROLS_FILE, DEFAULT_SCHEDULE_SETTINGS
        )
        
        results = validate_paths()
        
        if verbose:
            print("\n=== Path Validation Results ===")
            for path_name, path_value in results["paths"].items():
                status = "✓" if os.path.exists(path_value) else "✗"
                print(f"{status} {path_name}: {path_value}")
            
            if results["issues"]:
                print("\n=== Issues Found ===")
                for issue in results["issues"]:
                    print(f"- {issue}")
        
        # Try to fix issues if requested
        if fix and not results["success"]:
            fixed_issues = []
            
            # Ensure config directory exists
            if not os.path.exists(CONFIG_DIR):
                if ensure_directory_exists(CONFIG_DIR):
                    fixed_issues.append(f"Created config directory: {CONFIG_DIR}")
            
            # Ensure photos directory exists
            if not os.path.exists(PHOTOS_DIR):
                if ensure_directory_exists(PHOTOS_DIR, 0o777):
                    fixed_issues.append(f"Created photos directory: {PHOTOS_DIR}")
            
            # Copy default configuration files if needed
            if not os.path.exists(CAMERA_SETTINGS) and os.path.exists(DEFAULT_CAMERA_SETTINGS):
                try:
                    ensure_directory_exists(os.path.dirname(CAMERA_SETTINGS))
                    from shutil import copyfile
                    copyfile(DEFAULT_CAMERA_SETTINGS, CAMERA_SETTINGS)
                    fixed_issues.append(f"Copied default camera settings to: {CAMERA_SETTINGS}")
                except Exception as e:
                    results["issues"].append(f"Failed to copy camera settings: {e}")
            
            if not os.path.exists(CONTROLS_FILE) and os.path.exists(DEFAULT_CONTROLS_FILE):
                try:
                    ensure_directory_exists(os.path.dirname(CONTROLS_FILE))
                    from shutil import copyfile
                    copyfile(DEFAULT_CONTROLS_FILE, CONTROLS_FILE)
                    fixed_issues.append(f"Copied default controls to: {CONTROLS_FILE}")
                except Exception as e:
                    results["issues"].append(f"Failed to copy controls: {e}")
            
            if not os.path.exists(SCHEDULE_SETTINGS) and os.path.exists(DEFAULT_SCHEDULE_SETTINGS):
                try:
                    ensure_directory_exists(os.path.dirname(SCHEDULE_SETTINGS))
                    from shutil import copyfile
                    copyfile(DEFAULT_SCHEDULE_SETTINGS, SCHEDULE_SETTINGS)
                    fixed_issues.append(f"Copied default schedule settings to: {SCHEDULE_SETTINGS}")
                except Exception as e:
                    results["issues"].append(f"Failed to copy schedule settings: {e}")
            
            if fixed_issues:
                results["fixed"] = fixed_issues
                if verbose:
                    print("\n=== Fixed Issues ===")
                    for fixed in fixed_issues:
                        print(f"+ {fixed}")
                
                # Re-validate after fixes
                results = validate_paths()
        
        return results
    
    except ImportError as e:
        return {
            "success": False,
            "issues": [f"Failed to import path module: {e}"],
            "paths": {}
        }

def main():
    parser = argparse.ArgumentParser(description="Validate Creaturebox Web paths")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print detailed information")
    parser.add_argument("-f", "--fix", action="store_true", help="Attempt to fix issues")
    parser.add_argument("-j", "--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()
    
    results = validate_paths(args.verbose, args.fix)
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.verbose:
        if results["success"]:
            print("All paths validated successfully.")
        else:
            print(f"Validation failed with {len(results['issues'])} issues.")
            for issue in results["issues"]:
                print(f"- {issue}")
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    sys.exit(main())
