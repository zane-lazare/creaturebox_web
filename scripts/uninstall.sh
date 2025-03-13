#!/bin/bash

# Creaturebox Web Interface Uninstallation Script
# This script removes the Creaturebox Web Interface from a Raspberry Pi

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${RED}"
echo "=============================================="
echo "  Creaturebox Web Interface Uninstaller"
echo "=============================================="
echo -e "${NC}"

# Default installation directory
INSTALL_DIR="/opt/creaturebox_web"

# Ask for confirmation
read -p "Are you sure you want to uninstall the Creaturebox Web Interface? (y/N): " confirm
if [[ "$confirm" != [yY] && "$confirm" != [yY][eE][sS] ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# Ask if user wants to keep configuration and data
read -p "Do you want to keep configuration and data files? (Y/n): " keep_data
keep_data=${keep_data:-Y}

# Stop and disable the service
if [ -f /etc/systemd/system/creaturebox-web.service ]; then
    echo "Stopping and disabling Creaturebox Web service..."
    sudo systemctl stop creaturebox-web.service
    sudo systemctl disable creaturebox-web.service
    sudo rm /etc/systemd/system/creaturebox-web.service
    sudo systemctl daemon-reload
fi

# Remove Nginx configuration if present
if [ -f /etc/nginx/sites-enabled/creaturebox-web ]; then
    echo "Removing Nginx configuration..."
    sudo rm -f /etc/nginx/sites-enabled/creaturebox-web
    sudo rm -f /etc/nginx/sites-available/creaturebox-web
    sudo systemctl reload nginx
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    if [[ "$keep_data" == [yY] || "$keep_data" == [yY][eE][sS] ]]; then
        echo "Keeping configuration and data files..."
        # Create a backup of the data and configuration
        echo "Creating backup of configuration..."
        BACKUP_DIR="$HOME/creaturebox_web_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup .env and other configuration files
        if [ -f "$INSTALL_DIR/.env" ]; then
            cp "$INSTALL_DIR/.env" "$BACKUP_DIR/"
        fi
        
        # Backup any other data directories you want to preserve
        if [ -d "$INSTALL_DIR/data" ]; then
            cp -r "$INSTALL_DIR/data" "$BACKUP_DIR/"
        fi
        
        echo "Backup created at: $BACKUP_DIR"
    fi
    
    echo "Removing installation directory..."
    sudo rm -rf "$INSTALL_DIR"
fi

# Print success message
echo -e "${GREEN}"
echo "=============================================="
echo "  Uninstallation Complete!"
echo "=============================================="
echo -e "${NC}"

if [[ "$keep_data" == [yY] || "$keep_data" == [yY][eE][sS] ]]; then
    echo "Configuration and data have been backed up to: $BACKUP_DIR"
fi

echo "The Creaturebox Web Interface has been successfully uninstalled."
echo ""
