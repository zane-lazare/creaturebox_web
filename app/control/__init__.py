"""
Control Module

This module provides a web interface for hardware control scripts,
including camera control, lighting control, and system management.
"""

from flask import Blueprint, current_app, render_template, request, jsonify, abort
import os
import logging

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

# Development test route to diagnose script execution
@control_bp.route('/test_camera')
def test_camera():
    """Development test endpoint for camera functionality."""
    try:
        # Try to directly execute the camera script
        import subprocess
        import sys
        import os
        
        # Get repository root
        from app.utils.paths import get_app_root
        repo_root = get_app_root()
        
        # Construct script path
        script_path = os.path.join(repo_root, 'software', 'TakePhoto.py')
        print(f"[DEBUG] Testing direct script execution at: {script_path}")
        
        if not os.path.exists(script_path):
            return jsonify({
                'success': False,
                'error': f"Script not found at: {script_path}"
            })
        
        # Get Python executable
        python_exe = sys.executable
        
        # Execute directly
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode,
        })
    
    except Exception as e:
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
