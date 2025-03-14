"""
Script Inventory and Mapping Module

This module provides a comprehensive inventory of all hardware control scripts
and their parameters, execution patterns, and expected outputs.
"""

import os
import json
from pathlib import Path
from flask import current_app

from app.utils.paths import get_app_root, get_script_path as get_script_path_util

# Define script categories
SCRIPT_CATEGORIES = {
    "camera": "Camera control scripts",
    "light": "Lighting control scripts",
    "system": "System management scripts",
    "power": "Power management scripts",
    "config": "Configuration management scripts"
}

# Define the script inventory with metadata
SCRIPT_INVENTORY = {
    # Camera Control Scripts
    "TakePhoto.py": {
        "category": "camera",
        "description": "Takes a photo with the current camera settings",
        "path": "software/TakePhoto_wrapper.py",  # Using the wrapper for JSON output
        "requires_sudo": True,
        "timeout": 60,  # Seconds
        "parameters": [],
        "output_pattern": None,  # No pattern needed as it returns JSON
        "success_pattern": None,  # Success determined by JSON parsing
        "error_patterns": []  # Error determined by JSON parsing
    },
    
    "CheckCamera.py": {
        "category": "camera",
        "description": "Check if the camera is available and working",
        "path": "software/CheckCamera_wrapper.py",  # Using the wrapper for JSON output
        "requires_sudo": True,
        "timeout": 10,  # Seconds
        "parameters": [],
        "output_pattern": None,  # Outputs JSON
        "success_pattern": None,  # Success determined by JSON parsing
        "error_patterns": []  # Error determined by JSON parsing
    },
    
    # Light Control Scripts
    "Attract_On.py": {
        "category": "light",
        "description": "Turn on the attract lights",
        "path": "software/Attract_On.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Attract Lights On",
        "error_patterns": [
            r"Error:"
        ]
    },
    "Attract_Off.py": {
        "category": "light",
        "description": "Turn off the attract lights",
        "path": "software/Attract_Off.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Attract Lights Off",
        "error_patterns": [
            r"Error:"
        ]
    },
    "Flash_On.py": {
        "category": "light",
        "description": "Turn on the camera flash",
        "path": "software/Scripts/Flash_On.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Setup The Relay Module is \[success\]",
        "error_patterns": [
            r"Error:"
        ]
    },
    "Flash_Off.py": {
        "category": "light",
        "description": "Turn off the camera flash",
        "path": "software/Scripts/Flash_Off.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Setup The Relay Module is \[success\]",
        "error_patterns": [
            r"Error:"
        ]
    },
    
    # System Management Scripts
    "StartCron.py": {
        "category": "system",
        "description": "Start the cron scheduler for automated tasks",
        "path": "software/StartCron.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Cron service started successfully",
        "error_patterns": [
            r"Error starting cron service:"
        ]
    },
    "StopCron.py": {
        "category": "system",
        "description": "Stop the cron scheduler to prevent automated tasks",
        "path": "software/StopCron.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Cron service stopped successfully",
        "error_patterns": [
            r"Error stopping cron service:"
        ]
    },
    "StopScheduledShutdown.py": {
        "category": "system",
        "description": "Cancel any scheduled system shutdown",
        "path": "software/StopScheduledShutdown.py",
        "requires_sudo": True,
        "timeout": 10,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Canceled scheduled shutdown",
        "error_patterns": [
            r"Error:"
        ]
    },
    
    # Power Management Scripts
    "Measure_Power.py": {
        "category": "power",
        "description": "Measure current power consumption",
        "path": "software/Measure_Power.py",
        "requires_sudo": True,
        "timeout": 30,
        "parameters": [],
        "output_pattern": r"Current Power: (\d+\.\d+)",
        "success_pattern": r"Current Power:",
        "error_patterns": [
            r"Error:"
        ]
    },
    "TurnEverythingOff.py": {
        "category": "power",
        "description": "Turn off all components",
        "path": "software/TurnEverythingOff.py",
        "requires_sudo": True,
        "timeout": 30,
        "parameters": [],
        "output_pattern": None,
        "success_pattern": r"Everything turned off",
        "error_patterns": [
            r"Error:"
        ]
    }
}

def get_script_path(script_name):
    """
    Get the absolute path for a script.
    
    Args:
        script_name: The name of the script in the inventory
        
    Returns:
        The absolute path to the script
    """
    if script_name not in SCRIPT_INVENTORY:
        raise ValueError(f"Script '{script_name}' not found in inventory")
        
    # Try to use the utility function from paths module
    script_path = get_script_path_util(script_name)
    if script_path and os.path.exists(script_path):
        return script_path
    
    # Fallback to the inventory path
    app_root = get_app_root()
    relative_path = SCRIPT_INVENTORY[script_name]['path']
    
    return os.path.join(app_root, relative_path)

def get_scripts_by_category(category=None):
    """
    Get all scripts in a category, or all scripts if category is None.
    
    Args:
        category: The category to filter by, or None for all scripts
        
    Returns:
        Dictionary of script information filtered by category
    """
    if category:
        return {name: info for name, info in SCRIPT_INVENTORY.items() 
                if info['category'] == category}
    return SCRIPT_INVENTORY

def get_script_info(script_name):
    """
    Get detailed information about a script.
    
    Args:
        script_name: The name of the script in the inventory
        
    Returns:
        Dictionary containing script information or None if not found
    """
    return SCRIPT_INVENTORY.get(script_name)

def build_script_inventory_from_filesystem():
    """
    Scan the filesystem for scripts and build an inventory.
    This is a placeholder for future development to automatically
    discover and catalog scripts.
    
    Returns:
        Dictionary containing discovered scripts
    """
    # This would scan directories and identify scripts
    # For now, we return the static inventory
    return SCRIPT_INVENTORY
