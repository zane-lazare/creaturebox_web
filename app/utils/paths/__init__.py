"""
Paths Module - Central path configuration for Creaturebox Web

This module provides standardized paths for all components of the Creaturebox Web
application, ensuring consistent directory references throughout the codebase.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# User constants
USER = "creature"
USER_HOME = f"/home/{USER}"

# Core directory structure
APP_ROOT = "/opt/creaturebox_web"  # Application installation directory
CONFIG_DIR = f"{USER_HOME}/.config/creaturebox"  # User configuration directory
PHOTOS_DIR = f"{USER_HOME}/creaturebox_photos"  # Photo storage directory

# Configuration files
CAMERA_SETTINGS = os.path.join(CONFIG_DIR, "camera_settings.csv")
CONTROLS_FILE = os.path.join(CONFIG_DIR, "controls.txt")
SCHEDULE_SETTINGS = os.path.join(CONFIG_DIR, "schedule_settings.csv")

# Default configuration templates
DEFAULT_CONFIG_DIR = os.path.join(APP_ROOT, "config")
DEFAULT_CAMERA_SETTINGS = os.path.join(DEFAULT_CONFIG_DIR, "camera_settings.csv")
DEFAULT_CONTROLS_FILE = os.path.join(DEFAULT_CONFIG_DIR, "controls.txt")
DEFAULT_SCHEDULE_SETTINGS = os.path.join(DEFAULT_CONFIG_DIR, "schedule_settings.csv")

# Software directories
SOFTWARE_DIR = os.path.join(APP_ROOT, "software")
SCRIPTS_DIR = os.path.join(SOFTWARE_DIR, "Scripts")

def get_app_root():
    """
    Get the application root directory, with fallbacks for development environments.
    
    Returns:
        str: The application root directory path
    """
    # Check if running in production at /opt/creaturebox_web
    if os.path.exists(APP_ROOT):
        return APP_ROOT
    
    # Development fallback - try to detect repository root
    current_file = os.path.abspath(__file__)
    app_utils = os.path.dirname(os.path.dirname(current_file))
    app_dir = os.path.dirname(app_utils)
    repo_root = os.path.dirname(app_dir)
    
    if os.path.exists(os.path.join(repo_root, "app")) and \
       os.path.exists(os.path.join(repo_root, "software")):
        logger.debug(f"Using development path: {repo_root}")
        return repo_root
    
    # Last resort - use relative paths from current working directory
    logger.warning("Unable to determine application root, using current directory")
    return os.getcwd()

def get_config_dir():
    """
    Get the configuration directory with fallbacks.
    
    Returns:
        str: The configuration directory path
    """
    # Check if production config directory exists
    if os.path.exists(CONFIG_DIR):
        return CONFIG_DIR
    
    # Development fallback - try repository config directory
    repo_root = get_app_root()
    dev_config = os.path.join(repo_root, "config")
    
    if os.path.exists(dev_config):
        logger.debug(f"Using development config path: {dev_config}")
        return dev_config
    
    # Last resort - use default config directory
    return DEFAULT_CONFIG_DIR

def get_photos_dir():
    """
    Get the photos directory with fallbacks.
    
    Returns:
        str: The photos directory path
    """
    # Check if production photos directory exists
    if os.path.exists(PHOTOS_DIR):
        return PHOTOS_DIR
    
    # Development fallback - use a directory in the repository
    repo_root = get_app_root()
    dev_photos = os.path.join(repo_root, "data", "photos")
    
    # Create development photos directory if it doesn't exist
    if not os.path.exists(dev_photos):
        try:
            os.makedirs(dev_photos, exist_ok=True)
            logger.debug(f"Created development photos directory: {dev_photos}")
        except Exception as e:
            logger.warning(f"Could not create photos directory: {e}")
    
    logger.debug(f"Using development photos path: {dev_photos}")
    return dev_photos

def get_camera_settings_path():
    """
    Get the path to the camera settings file.
    
    Returns:
        str: The camera settings file path
    """
    config_dir = get_config_dir()
    camera_settings = os.path.join(config_dir, "camera_settings.csv")
    
    if os.path.exists(camera_settings):
        return camera_settings
    
    # Fallback to default template
    logger.warning(f"Camera settings not found at {camera_settings}, using default")
    return DEFAULT_CAMERA_SETTINGS

def get_controls_path():
    """
    Get the path to the controls file.
    
    Returns:
        str: The controls file path
    """
    config_dir = get_config_dir()
    controls = os.path.join(config_dir, "controls.txt")
    
    if os.path.exists(controls):
        return controls
    
    # Fallback to default template
    logger.warning(f"Controls file not found at {controls}, using default")
    return DEFAULT_CONTROLS_FILE

def get_schedule_settings_path():
    """
    Get the path to the schedule settings file.
    
    Returns:
        str: The schedule settings file path
    """
    config_dir = get_config_dir()
    schedule = os.path.join(config_dir, "schedule_settings.csv")
    
    if os.path.exists(schedule):
        return schedule
    
    # Fallback to default template
    logger.warning(f"Schedule settings not found at {schedule}, using default")
    return DEFAULT_SCHEDULE_SETTINGS

def get_dated_photos_dir(date_str=None):
    """
    Get or create a dated photos directory.
    
    Args:
        date_str: Date string in YYYY-MM-DD format, or None for today
        
    Returns:
        str: Path to the dated photos directory
    """
    import datetime
    
    # Use today's date if none provided
    if date_str is None:
        today = datetime.datetime.now()
        date_str = today.strftime("%Y-%m-%d")
    
    photos_dir = get_photos_dir()
    dated_dir = os.path.join(photos_dir, date_str)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(dated_dir):
        try:
            os.makedirs(dated_dir, exist_ok=True)
            # Set permissions
            try:
                os.chmod(dated_dir, 0o777)  # Read/write/execute for all
            except Exception as e:
                logger.warning(f"Could not set permissions on {dated_dir}: {e}")
        except Exception as e:
            logger.error(f"Could not create dated photos directory: {e}")
            return photos_dir  # Fallback to base photos directory
    
    return dated_dir

def ensure_directory_exists(path, permissions=0o755):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        permissions: Permissions to set (default: 0o755)
        
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            logger.error(f"Path exists but is not a directory: {path}")
            return False
        return True
    
    try:
        os.makedirs(path, mode=permissions, exist_ok=True)
        logger.info(f"Created directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def get_script_path(script_name):
    """
    Get the full path to a script in the software directory.
    
    Args:
        script_name: Name of the script (with or without .py extension)
        
    Returns:
        str: Full path to the script or None if not found
    """
    # Add .py extension if not present
    if not script_name.endswith('.py'):
        script_name += '.py'
    
    # Check main software directory
    script_path = os.path.join(SOFTWARE_DIR, script_name)
    if os.path.exists(script_path):
        return script_path
    
    # Check Scripts subdirectory
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if os.path.exists(script_path):
        return script_path
    
    # Development fallback
    repo_root = get_app_root()
    dev_script = os.path.join(repo_root, "software", script_name)
    if os.path.exists(dev_script):
        return dev_script
    
    dev_script = os.path.join(repo_root, "software", "Scripts", script_name)
    if os.path.exists(dev_script):
        return dev_script
    
    logger.warning(f"Script not found: {script_name}")
    return None

def validate_paths():
    """
    Validate that all required paths exist and are accessible.
    
    Returns:
        dict: Validation results with issues found
    """
    results = {
        "success": True,
        "issues": [],
        "paths": {}
    }
    
    # Check application paths
    app_root = get_app_root()
    if not os.path.exists(app_root):
        results["issues"].append(f"Application root not found: {app_root}")
        results["success"] = False
    results["paths"]["app_root"] = app_root
    
    # Check configuration paths
    config_dir = get_config_dir()
    if not os.path.exists(config_dir):
        results["issues"].append(f"Configuration directory not found: {config_dir}")
        results["success"] = False
    results["paths"]["config_dir"] = config_dir
    
    # Check camera settings
    camera_settings = get_camera_settings_path()
    if not os.path.exists(camera_settings):
        results["issues"].append(f"Camera settings not found: {camera_settings}")
        results["success"] = False
    results["paths"]["camera_settings"] = camera_settings
    
    # Check controls file
    controls = get_controls_path()
    if not os.path.exists(controls):
        results["issues"].append(f"Controls file not found: {controls}")
        results["success"] = False
    results["paths"]["controls"] = controls
    
    # Check photos directory
    photos_dir = get_photos_dir()
    if not os.path.exists(photos_dir):
        results["issues"].append(f"Photos directory not found: {photos_dir}")
        results["success"] = False
    elif not os.access(photos_dir, os.W_OK):
        results["issues"].append(f"Photos directory not writable: {photos_dir}")
        results["success"] = False
    results["paths"]["photos_dir"] = photos_dir
    
    return results
