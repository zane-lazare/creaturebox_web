"""
Utility functions for the Photos module.

Handles file operations, thumbnail generation, and metadata extraction.
"""

import os
import re
import time
import json
import hashlib
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Union
from werkzeug.utils import secure_filename
from flask import current_app, abort

# Try to import PIL for image processing
try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Try to import exifread for metadata extraction
try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

# Setup logging
logger = logging.getLogger(__name__)

# Constants
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}

# Determine the base directory for the application
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define thumbnail directory with absolute path
THUMBNAIL_DIR = os.path.join(BASE_DIR, 'instance', 'thumbnails')
THUMBNAIL_QUALITY = 85

def ensure_thumbnail_dir():
    """Ensure the thumbnail directory exists."""
    try:
        # Create main thumbnail directory
        os.makedirs(THUMBNAIL_DIR, exist_ok=True)
        
        # Create subdirectories for different sizes
        os.makedirs(os.path.join(THUMBNAIL_DIR, 'small'), exist_ok=True)
        os.makedirs(os.path.join(THUMBNAIL_DIR, 'medium'), exist_ok=True)
        os.makedirs(os.path.join(THUMBNAIL_DIR, 'large'), exist_ok=True)
        
        # Set appropriate permissions
        os.chmod(THUMBNAIL_DIR, 0o755)
        os.chmod(os.path.join(THUMBNAIL_DIR, 'small'), 0o755)
        os.chmod(os.path.join(THUMBNAIL_DIR, 'medium'), 0o755)
        os.chmod(os.path.join(THUMBNAIL_DIR, 'large'), 0o755)
        
        logger.info(f"Thumbnail directories created at {THUMBNAIL_DIR}")
        return True
    except Exception as e:
        logger.error(f"Error creating thumbnail directories: {str(e)}")
        # Fallback to a temporary directory if we can't create the intended one
        global THUMBNAIL_DIR
        THUMBNAIL_DIR = os.path.join('/tmp', 'creaturebox_thumbnails')
        os.makedirs(THUMBNAIL_DIR, exist_ok=True)
        os.makedirs(os.path.join(THUMBNAIL_DIR, 'small'), exist_ok=True)
        os.makedirs(os.path.join(THUMBNAIL_DIR, 'medium'), exist_ok=True)
        os.makedirs(os.path.join(THUMBNAIL_DIR, 'large'), exist_ok=True)
        logger.warning(f"Using fallback thumbnail directory: {THUMBNAIL_DIR}")
        return False

# Create thumbnail directories on module load
try:
    ensure_thumbnail_dir()
except Exception as e:
    logger.error(f"Failed to create thumbnail directories: {str(e)}")
    # Will use a fallback location when thumbnails are requested

def is_image_file(filename: str) -> bool:
    """Check if a file is an image based on its extension."""
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS

def get_safe_path(path: str, allowed_roots: List[str]) -> Optional[str]:
    """
    Validate and normalize a path to ensure it's within allowed directories.
    
    Args:
        path: The path to validate
        allowed_roots: List of allowed root directories
        
    Returns:
        Normalized path if valid, None otherwise
    """
    if not path:
        # Return the first valid root directory if no path specified
        for root in allowed_roots:
            if os.path.exists(root) and os.path.isdir(root):
                return root
        return None
    
    # Normalize path and convert to absolute
    norm_path = os.path.normpath(path)
    
    # Check if path is within any allowed root
    for root in allowed_roots:
        root_abs = os.path.abspath(root)
        path_abs = os.path.abspath(norm_path)
        
        # Check if path is within allowed root
        if path_abs == root_abs or path_abs.startswith(root_abs + os.sep):
            if os.path.exists(path_abs):
                return path_abs
    
    return None

def list_directory_contents(directory: str) -> List[Dict[str, Any]]:
    """
    List contents of a directory with metadata.
    
    Args:
        directory: Directory path to list
        
    Returns:
        List of dictionaries with file/directory information
    """
    contents = []
    
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                # Skip hidden files and directories
                if entry.name.startswith('.'):
                    continue
                
                try:
                    stat_info = entry.stat()
                    is_dir = entry.is_dir()
                    is_image = not is_dir and is_image_file(entry.name)
                    
                    item = {
                        'name': entry.name,
                        'path': entry.path,
                        'is_dir': is_dir,
                        'is_image': is_image,
                        'size': stat_info.st_size if not is_dir else None,
                        'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    }
                    
                    # Add directory-specific information
                    if is_dir:
                        try:
                            # Count items, but limit to avoid performance issues
                            item_count = 0
                            for _, _, _ in zip(range(100), os.scandir(entry.path), range(100)):
                                item_count += 1
                            item['item_count'] = item_count
                            item['has_more'] = item_count >= 100
                        except (PermissionError, OSError):
                            item['item_count'] = None
                            item['has_more'] = None
                    
                    contents.append(item)
                except (PermissionError, OSError) as e:
                    logger.warning(f"Error accessing {entry.path}: {str(e)}")
                    continue
    except (PermissionError, OSError) as e:
        logger.error(f"Error listing directory {directory}: {str(e)}")
        raise
    
    # Sort: directories first, then files by name
    contents.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    
    return contents

def get_thumbnail_path(image_path: str, size: Tuple[int, int]) -> str:
    """
    Get path for thumbnail of a specific size.
    
    Args:
        image_path: Path to the original image
        size: Thumbnail size as (width, height)
        
    Returns:
        Path where the thumbnail should be stored
    """
    # Create a unique filename based on original path and size
    file_hash = hashlib.md5(image_path.encode()).hexdigest()
    size_dir = 'medium'  # Default
    
    if size[0] <= 100:
        size_dir = 'small'
    elif size[0] >= 400:
        size_dir = 'large'
    
    filename = f"{file_hash}_{size[0]}x{size[1]}.jpg"
    return os.path.join(THUMBNAIL_DIR, size_dir, filename)

def create_thumbnail(image_path: str, thumbnail_path: str, size: Tuple[int, int]) -> None:
    """
    Create a thumbnail for an image.
    
    Args:
        image_path: Path to the original image
        thumbnail_path: Path where thumbnail should be saved
        size: Thumbnail size as (width, height)
        
    Raises:
        Exception: If thumbnail creation fails
    """
    if not PIL_AVAILABLE:
        raise ImportError("Pillow is required for thumbnail generation")
    
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
    
    try:
        with Image.open(image_path) as img:
            # Preserve orientation from EXIF if available
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                
                exif = dict(img._getexif().items())
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError, TypeError):
                # No EXIF data available or no orientation tag
                pass
            
            # Create thumbnail
            img.thumbnail(size, Image.LANCZOS)
            
            # Convert transparency to white background if needed
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                img = background
            
            # Save as JPEG with quality setting
            img.save(thumbnail_path, 'JPEG', quality=THUMBNAIL_QUALITY)
    except Exception as e:
        logger.error(f"Error creating thumbnail for {image_path}: {str(e)}")
        raise

def get_image_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with metadata information
    """
    metadata = {
        'filename': os.path.basename(image_path),
        'path': image_path,
        'size': os.path.getsize(image_path),
        'modified': datetime.fromtimestamp(os.path.getmtime(image_path)).isoformat(),
    }
    
    # Get basic image info using Pillow
    if PIL_AVAILABLE:
        try:
            with Image.open(image_path) as img:
                metadata['dimensions'] = img.size
                metadata['format'] = img.format
                metadata['mode'] = img.mode
        except Exception as e:
            logger.warning(f"Error reading image info with Pillow: {str(e)}")
    
    # Get EXIF data using exifread
    if EXIFREAD_AVAILABLE:
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                # Convert tag objects to strings
                exif = {}
                for tag, value in tags.items():
                    # Skip binary data
                    if tag.startswith('Thumbnail'):
                        continue
                    exif[tag] = str(value)
                
                if exif:
                    metadata['exif'] = exif
        except Exception as e:
            logger.warning(f"Error reading EXIF data: {str(e)}")
    
    return metadata
