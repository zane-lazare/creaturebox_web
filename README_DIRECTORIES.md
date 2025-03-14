# Creaturebox Web Directory Structure

This document explains the standardized directory structure used in the Creaturebox Web application.

## Overview

Creaturebox Web follows a standardized directory structure to ensure consistent file access across all components.
This document explains where different files are stored and how the application accesses them.

## Core Directories

### Application Installation

```
/opt/creaturebox_web/          # Main application installation
  ├── app/                     # Flask application
  ├── software/                # Hardware control scripts
  │    └── Scripts/            # Additional scripts
  ├── config/                  # Default configuration templates
  └── venv/                    # Python virtual environment
```

### User Configuration and Data

```
/home/creature/
  ├── .config/creaturebox/     # User configuration files (active)
  │    ├── camera_settings.csv # Camera configuration
  │    ├── controls.txt        # Control parameters
  │    └── schedule_settings.csv # Scheduling configuration
  │
  └── creaturebox_photos/      # Photo storage
       └── YYYY-MM-DD/         # Date-based folders
```

## Directory Usage

### Configuration Files

- **Primary Location**: `/home/creature/.config/creaturebox/`
- **Default Templates**: `/opt/creaturebox_web/config/`
- **Purpose**: Stores user-specific configuration files that control camera settings, scheduling, and other parameters.

### Photo Storage

- **Location**: `/home/creature/creaturebox_photos/`
- **Structure**: Photos are organized in date-based folders (YYYY-MM-DD)
- **Purpose**: Stores captured images in an organized structure.

### Software Scripts

- **Location**: `/opt/creaturebox_web/software/`
- **Additional Scripts**: `/opt/creaturebox_web/software/Scripts/`
- **Purpose**: Contains hardware control scripts, including camera control, light control, and system management.

## Path Resolution

The application uses a central path resolution module to ensure all components can find files regardless of environment:

1. **Production**: Uses the standard paths described above.
2. **Development**: Falls back to relative paths within the repository.
3. **Validation**: Includes tools to verify paths exist and are accessible.

## Directory Setup

The installation script automatically:

1. Creates the necessary directories if they don't exist
2. Copies default configuration files to the correct locations
3. Sets appropriate permissions for each directory
4. Updates paths in scripts to use the standardized structure

## Path Validation

Use the included validation tool to verify path configuration:

```bash
python scripts/validate_paths.py --verbose
```

This will check that all required directories exist and are accessible.

## Manual Path Updates

If you need to manually update paths in scripts, use the provided utility:

```bash
python scripts/update_takephoto.py /path/to/script.py
```

This will update the script to use the standardized paths.
