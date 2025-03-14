# Camera Control Module Fixes

This document summarizes the changes made to fix JSON formatting issues and modal dialog display problems in the Camera Control Module.

## Overview of Issues

1. **JSON Parsing Issues**: The TakePhoto.py and CheckCamera.py scripts were not producing JSON-formatted outputs, causing parsing errors when trying to display their results.

2. **Modal Dialog Formatting**: The modal dialog for displaying script results had formatting issues making it difficult to see the output.

3. **Path Resolution**: Inconsistent path resolution, especially between Windows development environment and Raspberry Pi production environment.

## Solutions Implemented

### 1. Wrapper Scripts

Created wrapper scripts that execute the original camera scripts and format their output as JSON:

- `TakePhoto_wrapper.py`
- `CheckCamera_wrapper.py`

These wrappers handle all error cases and ensure consistent JSON output regardless of what the original scripts produce.

### 2. Enhanced Script Executor

Updated the script executor to better handle JSON responses:

- Added robust JSON parsing with fallback to traditional output parsing
- Improved error logging with detailed debug information
- Enhanced handling of script execution results

### 3. Improved Modal Dialog

Enhanced the modal dialog for better display of script outputs:

- Added capability to toggle between formatted and raw output views
- Improved the styling for better readability
- Added proper error handling for non-JSON responses

### 4. Debug Interface

Created a comprehensive debug interface for diagnosing camera issues:

- Added `/control/camera/debug` route showing script paths and statuses
- Created paths validation and testing endpoints
- Added detailed documentation for troubleshooting

### 5. Path Validation and Auto-Fixes

Implemented a path validation script that can automatically fix common issues:

- `validate_paths.py` script for diagnosing and fixing path-related problems
- Checks for wrapper scripts and creates them if missing
- Sets proper executable permissions on scripts

### 6. Updated Deployment Scripts

Enhanced deployment and installation scripts to ensure all required files are included and properly configured:

- Updated `update_deployment.sh` to handle wrapper scripts
- Added proper permissions for all scripts
- Integrated path validation into the deployment process

### 7. Comprehensive Documentation

Added detailed troubleshooting documentation:

- Created `docs/troubleshooting/camera_issues.md` with common issues and solutions
- Added debug button to the Camera Control page
- Enhanced error messages with more helpful information

## Files Changed

1. `app/control/script_executor.py` - Enhanced for better JSON handling
2. `app/control/script_inventory.py` - Updated to use wrapper scripts
3. `app/control/camera_utils.py` - Improved to handle JSON formatted responses
4. `app/control/__init__.py` - Added debug routes and improved error handling
5. `app/templates/control/camera.html` - Enhanced modal dialog and added debug link
6. `app/templates/control/debug.html` - New debug page for camera diagnostics
7. `software/TakePhoto_wrapper.py` - New wrapper for TakePhoto.py
8. `software/CheckCamera_wrapper.py` - New wrapper for CheckCamera.py
9. `scripts/validate_paths.py` - New script for validating and fixing paths
10. `scripts/run_validation.sh` - New script to properly run validation with correct environment
11. `scripts/update_deployment.sh` - Updated for better deployment handling
12. `docs/troubleshooting/camera_issues.md` - New troubleshooting guide

## Usage Instructions

### For Developers

1. When making changes to camera-related functionality, be sure to test with the debug page.
2. Use the path validation script to check for path issues: `python scripts/validate_paths.py --verbose`
3. If adding new scripts, create corresponding wrapper scripts that output JSON.

### For Users

1. If experiencing issues with camera controls, click the "Debug" button on the Camera Control page.
2. Follow the troubleshooting steps in the documentation.
3. Use the "Toggle Raw Output" button in error dialogs to see detailed output.

### For System Administrators

1. When deploying, run the path validation script to check for issues: `bash scripts/run_validation.sh --verbose --fix`
2. Ensure proper permissions on all scripts: `chmod -R 755 /opt/creaturebox_web/software`
3. Check logs for detailed error information: `journalctl -u creaturebox-web -f`
