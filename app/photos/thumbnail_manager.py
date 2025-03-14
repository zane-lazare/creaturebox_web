"""
Thumbnail manager for the Photos module.

Handles thumbnail generation with background processing,
caching, and cleanup.
"""

import os
import time
import logging
import threading
from typing import Tuple, List, Dict, Any, Optional
from pathlib import Path

from app.photos import tasks
from app.photos.utils import (
    create_thumbnail, get_thumbnail_path, is_image_file,
    THUMBNAIL_DIR
)

# Set up logging
logger = logging.getLogger(__name__)

# Constants
THUMBNAIL_SIZES = {
    'small': (100, 100),
    'medium': (240, 240),
    'large': (480, 480),
    'xlarge': (800, 800),
}

# Lock for thread safety
thumbnail_lock = threading.Lock()


def initialize(base_dir: str) -> None:
    """Initialize the thumbnail manager with proper directories."""
    # Make sure thumbnail directories exist
    for size_name in THUMBNAIL_SIZES.keys():
        os.makedirs(os.path.join(THUMBNAIL_DIR, size_name), exist_ok=True)
    
    # Initialize the task system
    tasks.initialize(base_dir)
    
    logger.info(f"Thumbnail manager initialized with directory: {THUMBNAIL_DIR}")


def get_or_create_thumbnail(
    image_path: str, 
    size_name: str = 'medium',
    force_regenerate: bool = False,
    background: bool = True
) -> Dict[str, Any]:
    """
    Get or create a thumbnail for an image.
    
    Args:
        image_path: Path to the original image
        size_name: Size name ('small', 'medium', 'large')
        force_regenerate: Whether to force regeneration even if thumbnail exists
        background: Whether to generate the thumbnail in the background
        
    Returns:
        Dictionary with thumbnail information
    """
    if not is_image_file(image_path):
        return {
            'success': False,
            'error': 'Not an image file',
            'path': None,
            'ready': False,
            'task_id': None
        }
    
    # Get the thumbnail size
    size = THUMBNAIL_SIZES.get(size_name, THUMBNAIL_SIZES['medium'])
    
    # Get the thumbnail path
    thumbnail_path = get_thumbnail_path(image_path, size)
    
    # Check if thumbnail already exists and is newer than the source image
    thumbnail_exists = os.path.exists(thumbnail_path)
    
    # Check if we need to regenerate
    needs_regeneration = (
        force_regenerate or 
        not thumbnail_exists or 
        (os.path.getmtime(thumbnail_path) < os.path.getmtime(image_path) if thumbnail_exists else True)
    )
    
    # If the thumbnail exists and doesn't need regeneration, return it immediately
    if thumbnail_exists and not needs_regeneration:
        return {
            'success': True,
            'path': thumbnail_path,
            'ready': True,
            'task_id': None
        }
    
    # Check if we can generate it immediately or should delegate to background
    if not background or not needs_regeneration:
        try:
            # Generate the thumbnail immediately
            with thumbnail_lock:
                create_thumbnail(image_path, thumbnail_path, size)
            
            return {
                'success': True,
                'path': thumbnail_path,
                'ready': True,
                'task_id': None
            }
        except Exception as e:
            logger.error(f"Error creating thumbnail for {image_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'path': None,
                'ready': False,
                'task_id': None
            }
    else:
        # Generate the thumbnail in the background
        task_id = tasks.enqueue_task(
            'thumbnail', 
            _generate_thumbnail_task,
            image_path, thumbnail_path, size
        )
        
        return {
            'success': True,
            'path': thumbnail_path if os.path.exists(thumbnail_path) else None,
            'ready': os.path.exists(thumbnail_path),
            'task_id': task_id
        }


def _generate_thumbnail_task(
    image_path: str, 
    thumbnail_path: str, 
    size: Tuple[int, int]
) -> Dict[str, Any]:
    """
    Background task to generate a thumbnail.
    
    Args:
        image_path: Path to the original image
        thumbnail_path: Path to save the thumbnail
        size: Thumbnail size as (width, height)
        
    Returns:
        Result information
    """
    try:
        with thumbnail_lock:
            create_thumbnail(image_path, thumbnail_path, size)
        
        return {
            'success': True,
            'path': thumbnail_path,
            'image_path': image_path,
            'size': size
        }
    except Exception as e:
        logger.error(f"Error in thumbnail generation task for {image_path}: {str(e)}")
        return {
            'success': False,
            'path': thumbnail_path,
            'image_path': image_path,
            'size': size,
            'error': str(e)
        }


def generate_thumbnails_for_directory(
    directory_path: str,
    sizes: Optional[List[str]] = None,
    recursive: bool = False
) -> Dict[str, Any]:
    """
    Generate thumbnails for all images in a directory.
    
    Args:
        directory_path: Path to the directory
        sizes: List of thumbnail sizes to generate
        recursive: Whether to process subdirectories recursively
        
    Returns:
        Task information
    """
    # Default to all sizes if not specified
    if not sizes:
        sizes = list(THUMBNAIL_SIZES.keys())
    
    # Enqueue the batch task
    task_id = tasks.enqueue_task(
        'batch_thumbnails',
        _batch_thumbnail_generation_task,
        directory_path, sizes, recursive
    )
    
    return {
        'success': True,
        'task_id': task_id,
        'directory': directory_path,
        'sizes': sizes,
        'recursive': recursive
    }


def _batch_thumbnail_generation_task(
    directory_path: str,
    sizes: List[str],
    recursive: bool
) -> Dict[str, Any]:
    """
    Background task to generate thumbnails for a directory.
    
    Args:
        directory_path: Path to the directory
        sizes: List of thumbnail sizes to generate
        recursive: Whether to process subdirectories recursively
        
    Returns:
        Result information
    """
    results = {
        'success': True,
        'directory': directory_path,
        'images_processed': 0,
        'errors': 0,
        'skipped': 0
    }
    
    try:
        # Find all image files in the directory
        image_files = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if is_image_file(file):
                    image_files.append(os.path.join(root, file))
            
            # If not recursive, break after first iteration
            if not recursive:
                break
        
        # Generate thumbnails for each image
        for image_path in image_files:
            try:
                for size_name in sizes:
                    size = THUMBNAIL_SIZES.get(size_name)
                    if not size:
                        continue
                    
                    thumbnail_path = get_thumbnail_path(image_path, size)
                    
                    # Check if thumbnail needs regeneration
                    if os.path.exists(thumbnail_path) and os.path.getmtime(thumbnail_path) >= os.path.getmtime(image_path):
                        results['skipped'] += 1
                        continue
                    
                    # Generate the thumbnail
                    with thumbnail_lock:
                        create_thumbnail(image_path, thumbnail_path, size)
                    
                    results['images_processed'] += 1
                    
                    # Small sleep to avoid overwhelming the system
                    time.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Error generating thumbnail for {image_path}: {str(e)}")
                results['errors'] += 1
        
        return results
    
    except Exception as e:
        logger.error(f"Error in batch thumbnail generation task for {directory_path}: {str(e)}")
        results['success'] = False
        results['error'] = str(e)
        return results


def cleanup_thumbnails(max_age_days: int = 30) -> Dict[str, Any]:
    """
    Clean up unused thumbnails.
    
    Args:
        max_age_days: Maximum age of thumbnails to keep
        
    Returns:
        Cleanup results
    """
    task_id = tasks.enqueue_task(
        'cleanup_thumbnails',
        _cleanup_thumbnails_task,
        max_age_days
    )
    
    return {
        'success': True,
        'task_id': task_id,
        'max_age_days': max_age_days
    }


def _cleanup_thumbnails_task(max_age_days: int) -> Dict[str, Any]:
    """
    Background task to clean up unused thumbnails.
    
    Args:
        max_age_days: Maximum age of thumbnails to keep
        
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
        cutoff_time = time.time() - (max_age_days * 86400)
        
        # Process all thumbnail directories
        for size_name in THUMBNAIL_SIZES.keys():
            size_dir = os.path.join(THUMBNAIL_DIR, size_name)
            
            # Skip if directory doesn't exist
            if not os.path.exists(size_dir) or not os.path.isdir(size_dir):
                continue
            
            # Scan for old thumbnails
            for filename in os.listdir(size_dir):
                file_path = os.path.join(size_dir, filename)
                
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
                    
                    # Small sleep to avoid overwhelming the system
                    time.sleep(0.01)
        
        return results
    
    except Exception as e:
        logger.error(f"Error in thumbnail cleanup task: {str(e)}")
        results['success'] = False
        results['error'] = str(e)
        return results


def get_thumbnail_stats() -> Dict[str, Any]:
    """
    Get statistics about thumbnails.
    
    Returns:
        Statistics information
    """
    stats = {
        'success': True,
        'total_thumbnails': 0,
        'total_size_bytes': 0,
        'by_size': {}
    }
    
    try:
        # Process all thumbnail directories
        for size_name in THUMBNAIL_SIZES.keys():
            size_dir = os.path.join(THUMBNAIL_DIR, size_name)
            
            # Skip if directory doesn't exist
            if not os.path.exists(size_dir) or not os.path.isdir(size_dir):
                stats['by_size'][size_name] = {'count': 0, 'size_bytes': 0}
                continue
            
            # Count files and size
            count = 0
            size_bytes = 0
            
            for filename in os.listdir(size_dir):
                file_path = os.path.join(size_dir, filename)
                
                # Skip if not a file
                if not os.path.isfile(file_path):
                    continue
                
                # Count and add size
                count += 1
                size_bytes += os.path.getsize(file_path)
            
            # Add to statistics
            stats['by_size'][size_name] = {
                'count': count,
                'size_bytes': size_bytes
            }
            
            # Update totals
            stats['total_thumbnails'] += count
            stats['total_size_bytes'] += size_bytes
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting thumbnail statistics: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
