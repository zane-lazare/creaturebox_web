# Path Module Documentation

## Overview

The Paths module provides standardized path references for all components of the Creaturebox Web application. It ensures consistent file access across different environments and provides fallback mechanisms for development and testing.

## Core Constants

```python
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
```

## Key Functions

### `get_app_root()`

Returns the application root directory, with fallbacks for development environments.

```python
# Production: /opt/creaturebox_web
# Development: Repository root directory
```

### `get_config_dir()`

Returns the configuration directory with fallbacks.

```python
# Production: /home/creature/.config/creaturebox
# Development: Repository config directory
```

### `get_photos_dir()`

Returns the photos directory with fallbacks.

```python
# Production: /home/creature/creaturebox_photos
# Development: Repository data/photos directory
```

### `get_camera_settings_path()`, `get_controls_path()`, `get_schedule_settings_path()`

Returns the path to specific configuration files with fallbacks to default templates.

### `get_dated_photos_dir(date_str=None)`

Creates and returns a dated photos directory for organizing photos by date.

```python
# Example: /home/creature/creaturebox_photos/2023-01-15/
```

### `get_script_path(script_name)`

Returns the full path to a script in the software directory.

```python
# Searches in:
# 1. /opt/creaturebox_web/software/
# 2. /opt/creaturebox_web/software/Scripts/
# 3. Development fallbacks
```

### `validate_paths()`

Validates that all required paths exist and are accessible.

```python
# Returns a dictionary with:
# - success: Boolean indicating if all paths are valid
# - issues: List of issues found
# - paths: Dictionary of paths checked
```

## Usage Examples

### Getting Configuration Files

```python
from app.utils.paths import get_camera_settings_path

# Get the camera settings path
settings_path = get_camera_settings_path()

# Read the settings file
with open(settings_path, 'r') as f:
    # Process the file
    pass
```

### Working with Photos

```python
from app.utils.paths import get_photos_dir, get_dated_photos_dir

# Get the base photos directory
photos_dir = get_photos_dir()

# Get a dated directory for today
today_dir = get_dated_photos_dir()

# Save a photo in the dated directory
photo_path = os.path.join(today_dir, "my_photo.jpg")
```

### Executing Scripts

```python
from app.utils.paths import get_script_path
import subprocess

# Get the path to a script
script_path = get_script_path("TakePhoto.py")

# Execute the script
if script_path:
    subprocess.run(["python3", script_path], check=True)
```

### Path Validation

```python
from app.utils.paths import validate_paths

# Validate all paths
results = validate_paths()

if results["success"]:
    print("All paths are valid")
else:
    print("Issues found:")
    for issue in results["issues"]:
        print(f"- {issue}")
```

## Environment Detection

The module automatically detects the environment and adjusts paths accordingly:

1. **Production**: Uses standard paths in `/opt/creaturebox_web` and `/home/creature`
2. **Development**: Uses relative paths within the repository
3. **Fallbacks**: Each function includes fallback logic if primary paths don't exist

## Path Security

The module includes security features:

1. No use of `os.system()` or shell commands for path operations
2. No use of relative paths in final resolved paths
3. No use of unsanitized user input for path construction
4. Validation of paths before use

## Debugging

You can get detailed information about path resolution by enabling DEBUG level logging:

```python
import logging
logging.getLogger('app.utils.paths').setLevel(logging.DEBUG)
```

This will output detailed information about path resolution decisions.
