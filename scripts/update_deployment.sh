#!/bin/bash
# Update Creaturebox Web Interface Deployment
# This script updates the installed files from the repository

# Exit on any error
set -e

# Configuration
REPO_DIR="$HOME/creaturebox_web"
INSTALL_DIR="/opt/creaturebox_web"
SERVICE_NAME="creaturebox-web"

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Welcome message
echo -e "${GREEN}Creaturebox Web Interface - Deployment Update Script${NC}"
echo "This script will update the deployed application from your repository."
echo

# Confirm before proceeding
read -p "Do you want to proceed with the update? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${YELLOW}Update cancelled.${NC}"
    exit 0
fi

# Check if repository exists
if [ ! -d "$REPO_DIR" ]; then
    echo -e "${RED}Error: Repository directory $REPO_DIR does not exist.${NC}"
    exit 1
fi

# Check if installation exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}Error: Installation directory $INSTALL_DIR does not exist.${NC}"
    exit 1
fi

# Pull latest changes from repository
echo -e "${GREEN}Pulling latest changes from repository...${NC}"
cd "$REPO_DIR"
git pull

# Create backup of current installation
BACKUP_DIR="/tmp/creaturebox_web_backup_$(date +%Y%m%d%H%M%S)"
echo -e "${GREEN}Creating backup at $BACKUP_DIR...${NC}"
mkdir -p "$BACKUP_DIR"
sudo cp -r "$INSTALL_DIR/app" "$BACKUP_DIR/"

# Update installation files
echo -e "${GREEN}Updating installation files...${NC}"

# Update app directory
echo "Updating app directory..."
sudo cp -r "$REPO_DIR/app" "$INSTALL_DIR/"

# Update requirements
echo "Updating requirements..."
sudo cp "$REPO_DIR/requirements.txt" "$INSTALL_DIR/"

# Install any new requirements
echo -e "${GREEN}Installing new requirements...${NC}"
cd "$INSTALL_DIR"
source venv/bin/activate
pip install -r requirements.txt

# Restart service
echo -e "${GREEN}Restarting service...${NC}"
sudo systemctl restart "$SERVICE_NAME"

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo
echo -e "${GREEN}Update completed successfully!${NC}"
echo "If you encounter any issues, a backup was created at $BACKUP_DIR"
echo "You can restore it with: sudo cp -r $BACKUP_DIR/app $INSTALL_DIR/"
echo

# Final instructions
echo -e "${YELLOW}Important:${NC}"
echo "1. Check that the web interface is working correctly"
echo "2. If there are issues, check the logs with: sudo journalctl -u $SERVICE_NAME -f"
echo "3. You can restore the backup if needed with the command shown above"
echo
