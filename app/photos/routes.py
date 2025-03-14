"""
Photo routes for the Creaturebox Web Interface.

These routes handle photo browsing, viewing, and management.
"""

import os
import json
import datetime
import tempfile
from pathlib import Path
from flask import render_template, jsonify, current_app, request, send_file, abort, session, url_for
from werkzeug.utils import secure_filename
from app.photos import bp
from app.auth.decorators import login_required
from app.photos.utils import (
    get_safe_path, list_directory_contents, get_thumbnail_path,
    get_image_metadata, create_thumbnail, is_image_file,
    BASE_DIR
)
from app.photos import thumbnail_manager, tasks, download

# Configuration
# These will eventually move to a settings file

# Determine application base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define photo directories with fallbacks
APP_PHOTOS_DIR = os.path.join(BASE_DIR, 'instance', 'photos')  # App's photos directory

# Create app photos directory if it doesn't exist
try:
    os.makedirs(APP_PHOTOS_DIR, exist_ok=True)
    os.chmod(APP_PHOTOS_DIR, 0o755)  # Ensure directory is readable
except Exception as e:
    print(f"Error creating photos directory: {str(e)}")

PHOTO_ROOT_DIRS = [
    '/home/pi/creaturebox/images',  # Default Creaturebox images directory
    '/home/pi/mothbox/images',      # Default Mothbox images directory
    APP_PHOTOS_DIR                  # App's photos directory
]

# For testing on non-Pi systems
if not os.path.exists('/home/pi'):
    # Add user Pictures directory for testing
    PHOTO_ROOT_DIRS.append(os.path.join(os.path.expanduser('~'), 'Pictures'))

# Initialize the thumbnail manager
thumbnail_manager.initialize(BASE_DIR)

@bp.route('/')
@login_required
def index():
    """Render the photo browser main page."""
    return render_template('photos/index.html', title='Photo Browser')

@bp.route('/browser')
@login_required
def browser():
    """Render the photo browser interface."""
    return render_template('photos/browser.html', title='Photo Browser')

@bp.route('/viewer')
@login_required
def viewer():
    """Render the photo viewer interface."""
    path = request.args.get('path', '')
    return render_template('photos/viewer.html', title='Photo Viewer', path=path)

@bp.route('/api/directories')
@login_required
def api_list_directories():
    """List root directories available for browsing."""
    directories = []
    
    for root_dir in PHOTO_ROOT_DIRS:
        if os.path.exists(root_dir) and os.path.isdir(root_dir):
            directories.append({
                'path': root_dir,
                'name': os.path.basename(root_dir) or root_dir,
                'item_count': len(os.listdir(root_dir)) if os.access(root_dir, os.R_OK) else None
            })
    
    return jsonify({
        'success': True,
        'directories': directories
    })

@bp.route('/api/browse')
@login_required
def api_browse_directory():
    """Browse a directory and return its contents."""
    path = request.args.get('path', '')
    
    # Ensure the path is valid and within allowed directories
    safe_path = get_safe_path(path, PHOTO_ROOT_DIRS)
    if safe_path is None:
        return jsonify({
            'success': False,
            'message': 'Invalid directory path'
        }), 400
    
    try:
        contents = list_directory_contents(safe_path)
        return jsonify({
            'success': True,
            'path': safe_path,
            'contents': contents
        })
    except Exception as e:
        current_app.logger.error(f"Error browsing directory {safe_path}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/thumbnail')
@login_required
def api_get_thumbnail():
    """Generate and return a thumbnail for an image."""
    path = request.args.get('path', '')
    size = request.args.get('size', 'medium')  # small, medium, large
    force = request.args.get('force', '0') == '1'
    
    # Ensure the path is valid and within allowed directories
    safe_path = get_safe_path(path, PHOTO_ROOT_DIRS)
    if safe_path is None or not os.path.isfile(safe_path) or not is_image_file(safe_path):
        abort(404)
    
    try:
        # Get or create thumbnail
        result = thumbnail_manager.get_or_create_thumbnail(
            safe_path, 
            size_name=size,
            force_regenerate=force,
            background=(request.args.get('async', '1') == '1')
        )
        
        if not result['success']:
            current_app.logger.error(f"Error creating thumbnail for {safe_path}: {result.get('error')}")
            abort(500)
            
        if not result['ready']:
            # If thumbnail is not ready and being generated in background,
            # return a placeholder or fallback
            placeholder_path = os.path.join(current_app.static_folder, 'img', 'thumbnail-placeholder.svg')
            if os.path.exists(placeholder_path):
                return send_file(placeholder_path, mimetype='image/svg+xml')
            else:
                # If no placeholder exists, redirect to the original image
                return send_file(safe_path)
        
        # Send the thumbnail
        return send_file(result['path'], mimetype='image/jpeg')
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail for {safe_path}: {str(e)}")
        abort(500)

@bp.route('/api/image')
@login_required
def api_get_image():
    """Return the full-sized image."""
    path = request.args.get('path', '')
    
    # Ensure the path is valid and within allowed directories
    safe_path = get_safe_path(path, PHOTO_ROOT_DIRS)
    if safe_path is None or not os.path.isfile(safe_path) or not is_image_file(safe_path):
        abort(404)
    
    try:
        return send_file(safe_path)
    except Exception as e:
        current_app.logger.error(f"Error serving image {safe_path}: {str(e)}")
        abort(500)

@bp.route('/api/metadata')
@login_required
def api_get_metadata():
    """Return metadata for an image."""
    path = request.args.get('path', '')
    
    # Ensure the path is valid and within allowed directories
    safe_path = get_safe_path(path, PHOTO_ROOT_DIRS)
    if safe_path is None or not os.path.isfile(safe_path) or not is_image_file(safe_path):
        return jsonify({
            'success': False,
            'message': 'Invalid image path'
        }), 404
    
    try:
        metadata = get_image_metadata(safe_path)
        return jsonify({
            'success': True,
            'metadata': metadata
        })
    except Exception as e:
        current_app.logger.error(f"Error reading metadata for {safe_path}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/download')
@login_required
def api_download_image():
    """Download a single image file."""
    path = request.args.get('path', '')
    
    # Ensure the path is valid and within allowed directories
    safe_path = get_safe_path(path, PHOTO_ROOT_DIRS)
    if safe_path is None or not os.path.isfile(safe_path):
        abort(404)
    
    try:
        return send_file(safe_path, as_attachment=True, 
                        download_name=secure_filename(os.path.basename(safe_path)))
    except Exception as e:
        current_app.logger.error(f"Error downloading file {safe_path}: {str(e)}")
        abort(500)

@bp.route('/api/batch-download', methods=['POST'])
@login_required
def api_batch_download():
    """Create a ZIP archive for batch download."""
    try:
        # Get the list of images to download
        data = request.get_json()
        if not data or 'images' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing images list'
            }), 400
        
        images = data.get('images', [])
        download_name = data.get('filename', '')
        include_folders = data.get('include_folders', True)
        
        # Create the ZIP archive
        result = download.create_zip_archive(
            images=images,
            allowed_roots=PHOTO_ROOT_DIRS,
            download_filename=download_name,
            include_folders=include_folders
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Failed to create download')
            }), 500
        
        return jsonify({
            'success': True,
            'task_id': result['task_id'],
            'filename': result['filename'],
            'image_count': result['image_count']
        })
    except Exception as e:
        current_app.logger.error(f"Error creating batch download: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/api/download-status')
@login_required
def api_download_status():
    """Check the status of a batch download."""
    task_id = request.args.get('task_id', '')
    if not task_id:
        return jsonify({
            'success': False,
            'message': 'Missing task ID'
        }), 400
    
    # Get the task status
    status = tasks.get_task_status(task_id)
    
    if status['status'] == 'unknown':
        return jsonify({
            'success': False,
            'message': 'Unknown task ID'
        }), 404
    
    # Create a download URL if the task is completed
    download_url = None
    if status['status'] == tasks.STATUS_COMPLETED and 'result' in status:
        result = status['result']
        if result.get('success') and 'filename' in result:
            download_url = url_for('photos.api_download_archive', filename=result['filename'])
    
    return jsonify({
        'success': True,
        'status': status['status'],
        'download_url': download_url,
        'details': {
            key: value for key, value in status.items()
            if key not in ('func', 'args', 'kwargs')
        }
    })


@bp.route('/api/download-archive')
@login_required
def api_download_archive():
    """Download a previously created ZIP archive."""
    filename = request.args.get('filename', '')
    if not filename:
        abort(400)
    
    # Sanitize the filename to prevent path traversal
    filename = secure_filename(filename)
    
    # Get the download path
    file_path = download.get_download_path(filename)
    if not file_path:
        abort(404)
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        current_app.logger.error(f"Error sending download archive: {str(e)}")
        abort(500)


@bp.route('/api/generate-thumbnails', methods=['POST'])
@login_required
def api_generate_thumbnails():
    """Generate thumbnails for a directory."""
    try:
        # Get the directory and options
        data = request.get_json()
        if not data or 'directory' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing directory path'
            }), 400
        
        directory = data.get('directory', '')
        sizes = data.get('sizes', ['small', 'medium', 'large'])
        recursive = data.get('recursive', False)
        
        # Ensure the path is valid and within allowed directories
        safe_path = get_safe_path(directory, PHOTO_ROOT_DIRS)
        if safe_path is None or not os.path.isdir(safe_path):
            return jsonify({
                'success': False,
                'message': 'Invalid directory path'
            }), 400
        
        # Generate thumbnails
        result = thumbnail_manager.generate_thumbnails_for_directory(
            safe_path,
            sizes=sizes,
            recursive=recursive
        )
        
        return jsonify({
            'success': True,
            'task_id': result['task_id'],
            'directory': result['directory'],
            'sizes': result['sizes'],
            'recursive': result['recursive']
        })
    except Exception as e:
        current_app.logger.error(f"Error starting thumbnail generation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/api/task-status')
@login_required
def api_task_status():
    """Check the status of a task."""
    task_id = request.args.get('task_id', '')
    if not task_id:
        return jsonify({
            'success': False,
            'message': 'Missing task ID'
        }), 400
    
    # Get the task status
    status = tasks.get_task_status(task_id)
    
    if status['status'] == 'unknown':
        return jsonify({
            'success': False,
            'message': 'Unknown task ID'
        }), 404
    
    return jsonify({
        'success': True,
        'status': status['status'],
        'details': {
            key: value for key, value in status.items()
            if key not in ('func', 'args', 'kwargs')
        }
    })


@bp.route('/api/tasks')
@login_required
def api_list_tasks():
    """List all tasks."""
    task_type = request.args.get('type')
    
    # Get all tasks
    task_list = tasks.get_all_tasks(task_type)
    
    return jsonify({
        'success': True,
        'tasks': task_list
    })


@bp.route('/api/thumbnail-stats')
@login_required
def api_thumbnail_stats():
    """Get thumbnail statistics."""
    stats = thumbnail_manager.get_thumbnail_stats()
    
    return jsonify(stats)


@bp.route('/api/cleanup-thumbnails', methods=['POST'])
@login_required
def api_cleanup_thumbnails():
    """Clean up old thumbnails."""
    try:
        # Get the options
        data = request.get_json() or {}
        max_age_days = data.get('max_age_days', 30)
        
        # Start cleanup
        result = thumbnail_manager.cleanup_thumbnails(max_age_days)
        
        return jsonify({
            'success': True,
            'task_id': result['task_id'],
            'max_age_days': result['max_age_days']
        })
    except Exception as e:
        current_app.logger.error(f"Error starting thumbnail cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@bp.route('/api/cleanup-downloads', methods=['POST'])
@login_required
def api_cleanup_downloads():
    """Clean up old downloads."""
    try:
        # Get the options
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        # Start cleanup
        result = download.cleanup_downloads(max_age_hours)
        
        return jsonify({
            'success': True,
            'task_id': result['task_id'],
            'max_age_hours': result['max_age_hours']
        })
    except Exception as e:
        current_app.logger.error(f"Error starting download cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
