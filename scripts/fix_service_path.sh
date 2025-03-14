#!/bin/bash

# Fix for PATH environment in creaturebox-web service
# This script updates the systemd service file to include the full PATH

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Updating creaturebox-web service with full PATH environment...${NC}"

# Create backup of original service file
sudo cp /etc/systemd/system/creaturebox-web.service /etc/systemd/system/creaturebox-web.service.bak
echo "Backup created at: /etc/systemd/system/creaturebox-web.service.bak"

# Get actual path from current service file
CURRENT_PATH=$(grep "Environment=\"PATH=" /etc/systemd/system/creaturebox-web.service | sed 's/Environment="PATH=\(.*\)"/\1/')
INSTALL_DIR=$(grep "WorkingDirectory=" /etc/systemd/system/creaturebox-web.service | sed 's/WorkingDirectory=\(.*\)/\1/')

# Make sure we have the installation directory
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="/opt/creaturebox_web"
    echo "Could not find WorkingDirectory in service file, using default: $INSTALL_DIR"
fi

# Add full system path preserving current path
FULL_PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$CURRENT_PATH"

# Update the service file
sudo sed -i "s|Environment=\"PATH=.*\"|Environment=\"PATH=$FULL_PATH\"|" /etc/systemd/system/creaturebox-web.service

# Reload systemd and restart the service
echo "Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "Restarting creaturebox-web service..."
sudo systemctl restart creaturebox-web

# Check service status
echo -e "${YELLOW}Service status:${NC}"
sudo systemctl status creaturebox-web --no-pager

echo -e "${GREEN}Service update complete!${NC}"
echo "You can check logs with: sudo journalctl -u creaturebox-web -f"
