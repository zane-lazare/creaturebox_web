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

@control_bp.route('/camera')
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

@control_bp.route('/execute/<script_name>', methods=['POST'])
def execute(script_name):
    """
    Execute a script and return the result.
    
    Expected JSON input:
    {
        "parameters": [optional list of parameters],
        "async": true/false (optional, default is false)
    }
    """
    # Get script info
    script_info = get_script_info(script_name)
    if not script_info:
        abort(404, f"Script '{script_name}' not found")
    
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
    
    except Exception as e:
        logger.exception(f"Error executing script '{script_name}'")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@control_bp.route('/running')
def running_scripts():
    """Get list of currently running scripts."""
    running = get_running_scripts()
    return jsonify({
        'running_scripts': running
    })

def init_app(app):
    """Initialize the control module with the Flask app."""
    app.register_blueprint(control_bp)
    
    # Create template directories if they don't exist
    templates_dir = os.path.join(app.root_path, 'templates', 'control')
    os.makedirs(templates_dir, exist_ok=True)
    
    logger.info("Control module initialized")
