"""
Photo routes for the Creaturebox Web Interface.

These routes handle photo browsing, viewing, and management.
"""

import os
import json
import datetime
from pathlib import Path
from flask import render_template, jsonify, current_app, request, send_file, abort, session, url_for
from werkzeug.utils import secure_filename
from app.photos import bp
from app.auth.decorators import login_required
from app.photos.utils import (
    get_safe_path, list_directory_contents, get_thumbnail_path,
    get_image_metadata, create_thumbnail, is_image_file
)

# Configuration
# These will eventually move to a settings file
PHOTO_ROOT_DIRS = [
    '/home/pi/creaturebox/images',  # Default Creaturebox images directory
    '/home/pi/mothbox/images',      # Default Mothbox images directory
]

# For testing on non-Pi systems
if not os.path.exists('/home/pi'):
    PHOTO_ROOT_DIRS = [
        os.path.join(os.path.expanduser('~'), 'Pictures'),  # User's Pictures directory
        os.path.join(current_app.instance_path, 'photos') if 'current_app' in locals() else 'instance/photos',  # App's photos directory
    ]

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
    
    # Map size string to dimensions
    size_map = {
        'small': (100, 100),
        'medium': (240, 240),
        'large': (480, 480)
    }
    dimensions = size_map.get(size, size_map['medium'])
    
    # Ensure the path is valid and within allowed directories
    safe_path = get_safe_path(path, PHOTO_ROOT_DIRS)
    if safe_path is None or not os.path.isfile(safe_path) or not is_image_file(safe_path):
        abort(404)
    
    try:
        # Get or create thumbnail
        thumbnail_path = get_thumbnail_path(safe_path, dimensions)
        if not os.path.exists(thumbnail_path):
            create_thumbnail(safe_path, thumbnail_path, dimensions)
        
        # Send the thumbnail
        return send_file(thumbnail_path, mimetype='image/jpeg')
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
