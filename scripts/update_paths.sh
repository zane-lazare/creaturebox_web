#!/bin/bash

# Creaturebox Web Path Update Script
# This script updates all scripts to use the standardized path structure

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "========================================"
echo "  Creaturebox Web Path Update Script"
echo "========================================"
echo -e "${NC}"

# Get the application directory
if [ -d "/opt/creaturebox_web" ]; then
    APP_DIR="/opt/creaturebox_web"
else
    # Try to find in current directory
    APP_DIR=$(dirname "$(dirname "$(readlink -f "$0")")")
    echo -e "${YELLOW}Using app directory: ${APP_DIR}${NC}"
fi

# Check for creature user
if id "creature" &>/dev/null; then
    echo -e "${GREEN}Found creature user. ✓${NC}"
else
    echo -e "${YELLOW}Warning: The 'creature' user is not found on this system.${NC}"
    echo "This script requires the 'creature' user to be set up according to the Creaturebox protocol."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo "Creating directories..."
sudo mkdir -p /home/creature/.config/creaturebox
sudo mkdir -p /home/creature/creaturebox_photos

# Copy configuration files if they don't exist
echo "Checking configuration files..."
if [ ! -f "/home/creature/.config/creaturebox/camera_settings.csv" ] && [ -f "${APP_DIR}/config/camera_settings.csv" ]; then
    echo "Copying camera settings..."
    sudo cp -v "${APP_DIR}/config/camera_settings.csv" /home/creature/.config/creaturebox/
fi

if [ ! -f "/home/creature/.config/creaturebox/controls.txt" ] && [ -f "${APP_DIR}/config/controls.txt" ]; then
    echo "Copying controls file..."
    sudo cp -v "${APP_DIR}/config/controls.txt" /home/creature/.config/creaturebox/
fi

if [ ! -f "/home/creature/.config/creaturebox/schedule_settings.csv" ] && [ -f "${APP_DIR}/config/schedule_settings.csv" ]; then
    echo "Copying schedule settings..."
    sudo cp -v "${APP_DIR}/config/schedule_settings.csv" /home/creature/.config/creaturebox/
fi

# Create default controls.txt if it doesn't exist
if [ ! -f "/home/creature/.config/creaturebox/controls.txt" ]; then
    echo "Creating default controls.txt..."
    cat > /home/creature/.config/creaturebox/controls.txt << EOF
shutdown_enabled=True
minutes=60
OnlyFlash=False
LastCalibration=0
name=creaturebox
EOF
fi

# Set permissions
echo "Setting permissions..."
sudo chown -R creature:creature /home/creature/.config/creaturebox
sudo chmod -R 755 /home/creature/.config/creaturebox
sudo chown -R creature:creature /home/creature/creaturebox_photos
sudo chmod 777 /home/creature/creaturebox_photos

# Update paths in scripts
echo "Updating paths in scripts..."
find "${APP_DIR}/software" -type f -name "*.py" -exec sudo sed -i 's|/home/pi/Desktop/Mothbox|/home/creature/.config/creaturebox|g' {} \;
find "${APP_DIR}/software" -type f -name "*.py" -exec sudo sed -i 's|/home/pi/Desktop/Mothbox/photos|/home/creature/creaturebox_photos|g' {} \;
find "${APP_DIR}/software" -type f -name "*.py" -exec sudo sed -i 's|/home/pi/|/home/creature/|g' {} \;

# Set execute permissions
echo "Setting execute permissions on scripts..."
sudo chmod +x "${APP_DIR}/software/"*.py
sudo chmod +x "${APP_DIR}/software/Scripts/"*.py 2>/dev/null || true

# Check if Python is available
if command -v python3 &>/dev/null; then
    # Run the Python path validator
    echo "Running path validation..."
    cd "${APP_DIR}"
    python3 scripts/validate_paths.py --verbose --fix
else
    echo -e "${YELLOW}Warning: Python 3 not found, skipping path validation.${NC}"
fi

# Print success message
echo -e "${GREEN}"
echo "========================================"
echo "  Path Update Complete!"
echo "========================================"
echo -e "${NC}"
echo "Paths have been updated to use the standardized structure:"
echo "  - Configuration: /home/creature/.config/creaturebox/"
echo "  - Photos: /home/creature/creaturebox_photos/"
echo ""
echo "You may need to restart the creaturebox-web service for changes to take effect:"
echo "  sudo systemctl restart creaturebox-web"
echo ""
