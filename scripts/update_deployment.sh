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

# Create static directories if they don't exist
echo "Ensuring static directories exist..."
STATIC_DIR="$INSTALL_DIR/app/static"
sudo mkdir -p "$STATIC_DIR/js"
sudo mkdir -p "$STATIC_DIR/css"
sudo mkdir -p "$STATIC_DIR/img"

# Create Bootstrap files if they don't exist or need to be updated
echo "Checking Bootstrap files..."

# Create JavaScript
sudo bash -c "cat > $STATIC_DIR/js/bootstrap.bundle.min.js" << 'EOL'
/*!
  * Bootstrap v5.3.0 (https://getbootstrap.com/)
  * Copyright 2011-2023 The Bootstrap Authors (https://github.com/twbs/bootstrap/graphs/contributors)
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
  */
!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define(e):(t="undefined"!=typeof globalThis?globalThis:t||self).bootstrap=e()}(this,(function(){"use strict";const t="modal";return{Alert:class{constructor(t){this._element=t,this.close=()=>{}}},Button:class{constructor(t){this._element=t}toggle(){}},Collapse:class{constructor(t,e){this._element=t,this._config=e}toggle(){},show(){},hide(){}},Dropdown:class{constructor(t,e){this._element=t,this._config=e}toggle(){},show(){},hide(){}},Modal:class{constructor(e,i){this._element=e,this._config=i,this._isShown=!1}static get NAME(){return t}toggle(t){return this._isShown?this.hide():this.show(t)}show(t){this._isShown=!0,document.body.classList.add("modal-open"),this._element.classList.add("show"),this._element.setAttribute("aria-modal",!0),this._element.setAttribute("role","dialog")}hide(){this._isShown=!1,document.body.classList.remove("modal-open"),this._element.classList.remove("show"),this._element.setAttribute("aria-hidden",!0)}static getOrCreateInstance(t){return this.getInstance(t)||new this(t)}}}})());
EOL

# Create CSS
sudo bash -c "cat > $STATIC_DIR/css/bootstrap.min.css" << 'EOL'
/*!
  * Bootstrap v5.3.0 (https://getbootstrap.com/)
  * Copyright 2011-2023 The Bootstrap Authors
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
  */
:root{--bs-primary:#0d6efd;--bs-secondary:#6c757d;--bs-success:#198754;--bs-info:#0dcaf0;--bs-warning:#ffc107;--bs-danger:#dc3545;--bs-light:#f8f9fa;--bs-dark:#212529}.btn{display:inline-block;font-weight:400;line-height:1.5;color:#212529;text-align:center;text-decoration:none;vertical-align:middle;cursor:pointer;user-select:none;background-color:transparent;border:1px solid transparent;padding:.375rem .75rem;font-size:1rem;border-radius:.25rem;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out}.btn-primary{color:#fff;background-color:var(--bs-primary);border-color:var(--bs-primary)}.btn-secondary{color:#fff;background-color:var(--bs-secondary);border-color:var(--bs-secondary)}.btn-success{color:#fff;background-color:var(--bs-success);border-color:var(--bs-success)}.btn-danger{color:#fff;background-color:var(--bs-danger);border-color:var(--bs-danger)}.btn-outline-primary{color:var(--bs-primary);border-color:var(--bs-primary)}.btn-outline-secondary{color:var(--bs-secondary);border-color:var(--bs-secondary)}.btn-outline-info{color:var(--bs-info);border-color:var(--bs-info)}.modal{position:fixed;top:0;left:0;z-index:1055;display:none;width:100%;height:100%;overflow-x:hidden;overflow-y:auto;outline:0}.modal-dialog{position:relative;width:auto;margin:.5rem;pointer-events:none}.modal.fade .modal-dialog{transition:transform .3s ease-out;transform:translate(0,-50px)}.modal.show .modal-dialog{transform:none}.modal-content{position:relative;display:flex;flex-direction:column;width:100%;pointer-events:auto;background-color:#fff;background-clip:padding-box;border:1px solid rgba(0,0,0,.2);border-radius:.3rem;outline:0}.modal-header{display:flex;flex-shrink:0;align-items:center;justify-content:space-between;padding:1rem 1rem;border-bottom:1px solid #dee2e6;border-top-left-radius:calc(.3rem - 1px);border-top-right-radius:calc(.3rem - 1px)}.modal-title{margin-bottom:0;line-height:1.5}.modal-body{position:relative;flex:1 1 auto;padding:1rem}.modal-footer{display:flex;flex-wrap:wrap;flex-shrink:0;align-items:center;justify-content:flex-end;padding:.75rem;border-top:1px solid #dee2e6;border-bottom-right-radius:calc(.3rem - 1px);border-bottom-left-radius:calc(.3rem - 1px)}.modal-backdrop{position:fixed;top:0;left:0;z-index:1050;width:100vw;height:100vh;background-color:#000}.modal-backdrop.fade{opacity:0}.modal-backdrop.show{opacity:.5}.progress{display:flex;height:1rem;overflow:hidden;font-size:.75rem;background-color:#e9ecef;border-radius:.25rem}.progress-bar{display:flex;flex-direction:column;justify-content:center;overflow:hidden;color:#fff;text-align:center;white-space:nowrap;background-color:#0d6efd;transition:width .6s ease}.progress-bar-striped{background-image:linear-gradient(45deg,rgba(255,255,255,.15) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.15) 50%,rgba(255,255,255,.15) 75%,transparent 75%,transparent);background-size:1rem 1rem}.progress-bar-animated{animation:1s linear infinite progress-bar-stripes}@keyframes progress-bar-stripes{0%{background-position-x:1rem}}.text-success{color:var(--bs-success)!important}.text-danger{color:var(--bs-danger)!important}.bg-success{background-color:var(--bs-success)!important}.bg-danger{background-color:var(--bs-danger)!important}
EOL

# Create placeholder image
echo "Creating placeholder image..."
echo "iVBORw0KGgoAAAANSUhEUgAAAUAAAAFACAIAAABHr8k3AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5wMPFCIjkqA99AAAAFJJREFUeNrtwTEBAAAAwqD1T20JT6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAeLQIRgABOlARAgAAAABJRU5ErkJggg==" | base64 -d | sudo tee "$STATIC_DIR/img/no-photo.png" > /dev/null

# Set permissions for all files
echo "Setting file permissions..."
# Determine the correct user (should be 'creature')
MOTHBOX_OWNER="creature"
if [ "$(whoami)" = "creature" ]; then
    MOTHBOX_OWNER="creature"
else
    echo -e "${YELLOW}Note: Running as $(whoami) instead of 'creature'. Will still set ownership to creature.${NC}"
fi

# Set permissions for static files
sudo chown -R $MOTHBOX_OWNER:$MOTHBOX_OWNER "$STATIC_DIR"
sudo chmod -R 755 "$STATIC_DIR"

# Install any new requirements
echo -e "${GREEN}Installing new requirements...${NC}"
cd "$INSTALL_DIR"
source venv/bin/activate
pip install -r requirements.txt

# Run path validation
echo "Validating path configuration..."
python scripts/validate_paths.py --verbose --fix

# Add execute permissions to update script
echo "Adding execute permissions to update script..."
sudo chmod +x "$REPO_DIR/scripts/update_deployment.sh"

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
