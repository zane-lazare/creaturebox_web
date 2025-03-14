"""
Control Module

This module provides a web interface for hardware control scripts,
including camera control, lighting control, and system management.
"""

from flask import Blueprint, current_app, render_template, request, jsonify, abort
import os
import sys
import logging
import json

from .script_inventory import (
    get_scripts_by_category,
    get_script_info,
    SCRIPT_CATEGORIES
)
from .script_executor import (
    execute_script,
    execute_script_async,
    check_script_conflicts,
    get_running_scripts,
    ScriptExecutionError
)
from .camera_utils import check_camera_status, get_camera_settings

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
control_bp = Blueprint('control', __name__, url_prefix='/control')

@control_bp.route('/')
def index():
    """Control module main page."""
    return render_template('control/index.html', 
                          script_categories=SCRIPT_CATEGORIES,
                          scripts_by_category={
                              category: get_scripts_by_category(category)
                              for category in SCRIPT_CATEGORIES
                          })

@control_bp.route('/camera/status')
def camera_status():
    """Get camera status and information."""
    status = check_camera_status()
    settings = get_camera_settings()
    
    return jsonify({
        'camera': status,
        'settings': settings
    })

@control_bp.route('/camera', methods=['GET'])
def camera():
    """Camera control interface."""
    camera_scripts = get_scripts_by_category('camera')
    return render_template('control/camera.html', 
                          camera_scripts=camera_scripts)

@control_bp.route('/light')
def light():
    """Light control interface."""
    light_scripts = get_scripts_by_category('light')
    return render_template('control/light.html', 
                          light_scripts=light_scripts)

@control_bp.route('/system')
def system():
    """System control interface."""
    system_scripts = get_scripts_by_category('system')
    return render_template('control/system.html', 
                          system_scripts=system_scripts)

@control_bp.route('/power')
def power():
    """Power management interface."""
    power_scripts = get_scripts_by_category('power')
    return render_template('control/power.html', 
                          power_scripts=power_scripts)

@control_bp.route('/execute/<script_name>', methods=['POST', 'GET'])
def execute(script_name):
    """
    Execute a script and return the result.
    
    Expected JSON input:
    {
        "parameters": [optional list of parameters],
        "async": true/false (optional, default is false)
    }
    """
    logger.info(f"Received request to execute script: {script_name}")
    # Get script info
    script_info = get_script_info(script_name)
    if not script_info:
        error_msg = f"Script '{script_name}' not found in inventory"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 404
    
    # Parse request
    data = request.get_json() or {}
    parameters = data.get('parameters', [])
    async_execution = data.get('async', False)
    
    # Check for conflicts
    has_conflict, conflict_description = check_script_conflicts(script_name)
    if has_conflict:
        return jsonify({
            'success': False,
            'error': f"Conflict detected: {conflict_description}",
            'conflict': True
        }), 409  # Conflict status code
    
    try:
        if async_execution:
            # Start script execution in a separate thread
            execute_script_async(script_name, parameters)
            return jsonify({
                'success': True,
                'message': f"Script '{script_name}' started successfully",
                'async': True
            })
        else:
            # Execute script synchronously
            result = execute_script(script_name, parameters)
            
            if result.success:
                return jsonify({
                    'success': True,
                    'output': result.output,
                    'parsed_output': result.parsed_output,
                    'execution_time': result.execution_time
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.error,
                    'output': result.output,
                    'execution_time': result.execution_time
                }), 500  # Internal server error
    
    except FileNotFoundError as e:
        error_msg = f"Script file not found: {str(e)}"
        logger.exception(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 404
    except Exception as e:
        error_msg = f"Error executing script '{script_name}': {str(e)}"
        logger.exception(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@control_bp.route('/running')
def running_scripts():
    """Get list of currently running scripts."""
    running = get_running_scripts()
    return jsonify({
        'running_scripts': running
    })

# Camera debug route
@control_bp.route('/camera/debug')
def camera_debug():
    """Debug endpoint for camera functionality"""
    try:
        # Collect debug information
        debug_info = {
            "environment": {
                "app_root": get_app_root(),
                "config_dir": get_config_dir(),
                "python_version": sys.version,
                "platform": sys.platform
            },
            "scripts": {}
        }
        
        # Check all camera scripts
        for script_name in ["TakePhoto.py", "CheckCamera.py", "TakePhoto_wrapper.py", "CheckCamera_wrapper.py"]:
            script_path = get_script_path(script_name)
            script_exists = os.path.exists(script_path) if script_path else False
            
            debug_info["scripts"][script_name] = {
                "path": script_path,
                "exists": script_exists,
                "info": get_script_info(script_name)
            }
            
            # Try to run CheckCamera.py as a test
            if script_name == "CheckCamera.py" and script_exists:
                result = execute_script(script_name)
                debug_info["camera_check"] = {
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                }
        
        return render_template("control/debug.html", debug_info=debug_info)
    
    except Exception as e:
        logger.exception(f"Error in camera debug: {e}")
        return f"Error in debug endpoint: {str(e)}"

# Test paths route
@control_bp.route('/test_paths')
def test_paths():
    """Test path resolution for scripts"""
    try:
        from app.utils.paths import validate_paths, get_script_path
        
        # Validate all paths
        path_validation = validate_paths()
        
        # Check specific script paths
        script_paths = {}
        for script_name in ["TakePhoto.py", "CheckCamera.py", "TakePhoto_wrapper.py", "CheckCamera_wrapper.py"]:
            script_path = get_script_path(script_name)
            script_paths[script_name] = {
                "path": script_path,
                "exists": os.path.exists(script_path) if script_path else False
            }
        
        return jsonify({
            "success": path_validation["success"],
            "path_validation": path_validation,
            "script_paths": script_paths
        })
    except Exception as e:
        logger.exception(f"Error testing paths: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

# Development test route to diagnose script execution
@control_bp.route('/test_camera')
def test_camera():
    """Development test endpoint for camera functionality."""
    try:
        import os
        import sys
        import subprocess
        from app.utils.paths import get_app_root, get_script_path, get_config_dir
        
        # Get information about the environment
        info = {
            'environment': {
                'cwd': os.getcwd(),
                'python_executable': sys.executable,
                'platform': sys.platform
            }
        }
        
        # Test the path resolution
        app_root = get_app_root()
        info['app_root'] = app_root
        
        # Check script existence
        script_paths = {}
        for script_name in ["TakePhoto.py", "CheckCamera.py", "TakePhoto_wrapper.py", "CheckCamera_wrapper.py"]:
            script_path = get_script_path(script_name)
            script_paths[script_name] = {
                "path": script_path,
                "exists": os.path.exists(script_path) if script_path else False
            }
        info['script_paths'] = script_paths
        
        # Try to run the wrapper script directly
        wrapper_path = get_script_path("TakePhoto_wrapper.py")
        if wrapper_path and os.path.exists(wrapper_path):
            try:
                # Run the script with a timeout
                result = subprocess.run(
                    [sys.executable, wrapper_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                info['wrapper_execution'] = {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode
                }
                
                # Try to parse JSON output
                try:
                    json_result = json.loads(result.stdout)
                    info['json_parsed'] = json_result
                except json.JSONDecodeError as e:
                    info['json_parse_error'] = str(e)
            except Exception as e:
                info['wrapper_execution_error'] = str(e)
        else:
            info['wrapper_missing'] = True
        
        return jsonify(info)
    
    except Exception as e:
        logger.exception(f"Error in test_camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def init_app(app):
    """Initialize the control module with the Flask app."""
    app.register_blueprint(control_bp)
    
    # Create template directories if they don't exist
    templates_dir = os.path.join(app.root_path, 'templates', 'control')
    os.makedirs(templates_dir, exist_ok=True)
    
    logger.info("Control module initialized")
