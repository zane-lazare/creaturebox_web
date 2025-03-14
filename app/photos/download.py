"""
Download handler for the Photos module.

Provides functionality for single and batch downloads of images.
"""

import os
import time
import zipfile
import logging
import tempfile
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.photos import tasks
from app.photos.utils import get_safe_path, is_image_file

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_BATCH_NAME = "photo_download"

# Lock for thread safety
download_lock = threading.Lock()


def create_zip_archive(
    images: List[str],
    allowed_roots: List[str],
    download_filename: Optional[str] = None,
    include_folders: bool = True
) -> Dict[str, Any]:
    """
    Create a ZIP archive for batch download.
    
    Args:
        images: List of image paths to include
        allowed_roots: List of allowed root directories
        download_filename: Filename for the download archive
        include_folders: Whether to preserve folder structure
        
    Returns:
        Information about the created archive
    """
    # Generate a unique filename if not provided
    if not download_filename:
        download_filename = f"{DEFAULT_BATCH_NAME}_{int(time.time())}.zip"
    
    # Ensure the filename ends with .zip
    if not download_filename.lower().endswith('.zip'):
        download_filename += '.zip'
    
    # Sanitize the paths for security
    safe_images = []
    for path in images:
        safe_path = get_safe_path(path, allowed_roots)
        if safe_path and os.path.isfile(safe_path) and is_image_file(safe_path):
            safe_images.append(safe_path)
    
    # If no valid images found, return an error
    if not safe_images:
        return {
            'success': False,
            'error': 'No valid images found',
            'task_id': None
        }
    
    # Enqueue the batch download task
    task_id = tasks.enqueue_task(
        'batch_download',
        _create_zip_archive_task,
        safe_images, download_filename, include_folders
    )
    
    return {
        'success': True,
        'task_id': task_id,
        'filename': download_filename,
        'image_count': len(safe_images)
    }


def _create_zip_archive_task(
    images: List[str],
    download_filename: str,
    include_folders: bool
) -> Dict[str, Any]:
    """
    Background task to create a ZIP archive.
    
    Args:
        images: List of image paths to include
        download_filename: Filename for the download archive
        include_folders: Whether to preserve folder structure
        
    Returns:
        Result information
    """
    results = {
        'success': False,
        'filename': download_filename,
        'image_count': len(images),
        'archive_size': 0,
        'failed_images': []
    }
    
    if not images:
        results['error'] = 'No images to process'
        return results
    
    try:
        # Create a temporary file for the ZIP archive
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = temp_file.name
        
        # Create the ZIP archive
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for image_path in images:
                try:
                    # Determine the path inside the archive
                    if include_folders:
                        # Use just the filename without the full path
                        arcname = os.path.basename(image_path)
                    else:
                        # Use the full relative path structure
                        # Extract the common prefix from the first allowed root that matches
                        arcname = image_path
                    
                    # Add the file to the archive
                    zip_file.write(image_path, arcname=arcname)
                    
                except Exception as e:
                    logger.error(f"Error adding {image_path} to ZIP archive: {str(e)}")
                    results['failed_images'].append({
                        'path': image_path,
                        'error': str(e)
                    })
        
        # Move the temporary file to the download location
        download_dir = os.path.join(tempfile.gettempdir(), 'creaturebox_downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        final_path = os.path.join(download_dir, download_filename)
        
        # Ensure we don't overwrite an existing file
        counter = 1
        while os.path.exists(final_path):
            base_name, ext = os.path.splitext(download_filename)
            new_filename = f"{base_name}_{counter}{ext}"
            final_path = os.path.join(download_dir, new_filename)
            counter += 1
        
        # Move the file
        os.replace(temp_path, final_path)
        
        # Update results
        results['success'] = True
        results['archive_path'] = final_path
        results['archive_size'] = os.path.getsize(final_path)
        results['filename'] = os.path.basename(final_path)
        
        return results
    
    except Exception as e:
        logger.error(f"Error creating ZIP archive: {str(e)}")
        
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        
        results['error'] = str(e)
        return results


def get_download_path(filename: str) -> Optional[str]:
    """
    Get the full path for a download file.
    
    Args:
        filename: Name of the download file
        
    Returns:
        Full path to the file or None if not found
    """
    download_dir = os.path.join(tempfile.gettempdir(), 'creaturebox_downloads')
    file_path = os.path.join(download_dir, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return file_path
    
    return None


def cleanup_downloads(max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Clean up old downloads.
    
    Args:
        max_age_hours: Maximum age of downloads to keep in hours
        
    Returns:
        Cleanup results
    """
    task_id = tasks.enqueue_task(
        'cleanup_downloads',
        _cleanup_downloads_task,
        max_age_hours
    )
    
    return {
        'success': True,
        'task_id': task_id,
        'max_age_hours': max_age_hours
    }


def _cleanup_downloads_task(max_age_hours: int) -> Dict[str, Any]:
    """
    Background task to clean up old downloads.
    
    Args:
        max_age_hours: Maximum age of downloads to keep in hours
        
    Returns:
        Result information
    """
    results = {
        'success': True,
        'files_removed': 0,
        'bytes_freed': 0
    }
    
    try:
        # Calculate cutoff time
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Get the download directory
        download_dir = os.path.join(tempfile.gettempdir(), 'creaturebox_downloads')
        
        # Skip if directory doesn't exist
        if not os.path.exists(download_dir) or not os.path.isdir(download_dir):
            return results
        
        # Scan for old download files
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            
            # Skip if not a file
            if not os.path.isfile(file_path):
                continue
            
            # Check file modification time
            if os.path.getmtime(file_path) < cutoff_time:
                # Get file size before removing
                file_size = os.path.getsize(file_path)
                
                # Remove the file
                os.remove(file_path)
                
                # Update results
                results['files_removed'] += 1
                results['bytes_freed'] += file_size
        
        return results
    
    except Exception as e:
        logger.error(f"Error in download cleanup task: {str(e)}")
        results['success'] = False
        results['error'] = str(e)
        return results
