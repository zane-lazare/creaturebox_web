"""
System routes for the Creaturebox Web Interface.

These routes handle system monitoring, log viewing, and system controls.
"""

from flask import render_template, jsonify, current_app, request, send_file, abort, session
import os
import psutil
import platform
import json
import datetime
import subprocess
from pathlib import Path
import io
import re
from app.system import bp
from app.auth.decorators import login_required
from app.system.utils import (
    get_system_metrics, get_disk_usage, 
    get_temperature, get_uptime,
    get_logs, filter_logs, get_log_file_list
)

@bp.route('/metrics')
@login_required
def metrics():
    """Render the system metrics dashboard."""
    return render_template('system/metrics.html', title='System Metrics')

@bp.route('/api/metrics')
@login_required
def api_metrics():
    """Return JSON with current system metrics."""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # If not AJAX and not authenticated, return JSON error instead of redirect
    if not is_ajax and 'authenticated' not in session:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 401
        
    metrics = get_system_metrics()
    return jsonify(metrics)

@bp.route('/logs')
@login_required
def logs():
    """Render the log viewer interface."""
    log_files = get_log_file_list()
    return render_template('system/logs.html', title='Log Viewer', log_files=log_files)

@bp.route('/api/logs')
@login_required
def api_logs():
    """Return filtered log entries."""
    log_file = request.args.get('file', 'creaturebox.log')
    severity = request.args.get('severity', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    
    logs = get_logs(log_file)
    filtered_logs = filter_logs(logs, severity, start_date, end_date, search)
    
    # Pagination
    total = len(filtered_logs)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_logs = filtered_logs[start:end]
    
    return jsonify({
        'logs': paginated_logs,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })

@bp.route('/api/logs/download')
@login_required
def download_log():
    """Download a log file."""
    log_file = request.args.get('file', '')
    if not log_file or '..' in log_file:
        abort(400)
    
    app_log_path = Path(current_app.root_path).parent / 'logs' / log_file
    system_log_path = Path('/var/log') / log_file
    
    if app_log_path.exists():
        return send_file(app_log_path, as_attachment=True)
    elif system_log_path.exists():
        return send_file(system_log_path, as_attachment=True)
    else:
        abort(404)

@bp.route('/controls')
@login_required
def controls():
    """Render the system controls interface."""
    return render_template('system/controls.html', title='System Controls')

@bp.route('/api/controls/restart-service', methods=['POST'])
@login_required
def restart_service():
    """Restart a specific service."""
    service = request.json.get('service', '')
    allowed_services = ['creaturebox', 'nginx']
    
    if not service or service not in allowed_services:
        return jsonify({'success': False, 'message': 'Invalid service'}), 400
    
    try:
        # Using subprocess with explicit arguments for security
        result = subprocess.run(
            ['sudo', 'systemctl', 'restart', service],
            capture_output=True, text=True, timeout=10, check=True
        )
        return jsonify({
            'success': True,
            'message': f'Service {service} restarted successfully'
        })
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Error restarting service {service}: {e.stderr}")
        return jsonify({
            'success': False,
            'message': f'Error restarting service: {e.stderr}'
        }), 500
    except Exception as e:
        current_app.logger.error(f"Exception during service restart: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/controls/reboot', methods=['POST'])
@login_required
def reboot_system():
    """Reboot the system."""
    try:
        # Schedule a reboot in 1 minute to allow the response to be sent
        subprocess.run(
            ['sudo', 'shutdown', '-r', '+1', '"Reboot requested from web interface"'],
            capture_output=True, text=True, check=True
        )
        return jsonify({
            'success': True,
            'message': 'System will reboot in 1 minute'
        })
    except Exception as e:
        current_app.logger.error(f"Error during system reboot: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/controls/shutdown', methods=['POST'])
@login_required
def shutdown_system():
    """Shutdown the system."""
    try:
        # Schedule a shutdown in 1 minute to allow the response to be sent
        subprocess.run(
            ['sudo', 'shutdown', '+1', '"Shutdown requested from web interface"'],
            capture_output=True, text=True, check=True
        )
        return jsonify({
            'success': True,
            'message': 'System will shutdown in 1 minute'
        })
    except Exception as e:
        current_app.logger.error(f"Error during system shutdown: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/controls/cancel-shutdown', methods=['POST'])
@login_required
def cancel_shutdown():
    """Cancel a pending shutdown or reboot."""
    try:
        subprocess.run(
            ['sudo', 'shutdown', '-c'],
            capture_output=True, text=True, check=True
        )
        return jsonify({
            'success': True,
            'message': 'Scheduled shutdown or reboot cancelled'
        })
    except Exception as e:
        current_app.logger.error(f"Error cancelling shutdown: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/controls/service-status')
@login_required
def service_status():
    """Check if a service is active."""
    service = request.args.get('service', '')
    allowed_services = ['creaturebox', 'nginx', 'creaturebox_web']
    
    if not service or service not in allowed_services:
        return jsonify({'success': False, 'message': 'Invalid service'}), 400
    
    try:
        # Using subprocess with explicit arguments for security
        result = subprocess.run(
            ['systemctl', 'is-active', service],
            capture_output=True, text=True, timeout=5
        )
        return jsonify({
            'success': True,
            'active': result.returncode == 0,
            'status': result.stdout.strip()
        })
    except Exception as e:
        current_app.logger.error(f"Error checking service status {service}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
