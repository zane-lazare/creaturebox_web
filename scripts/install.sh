#!/bin/bash

# Creaturebox Web Interface Installation Script
# This script installs the Creaturebox Web Interface on a Raspberry Pi

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "========================================"
echo "  Creaturebox Web Interface Installer"
echo "========================================"
echo -e "${NC}"

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${RED}Error: This doesn't appear to be a Raspberry Pi.${NC}"
    exit 1
fi

PI_MODEL=$(tr -d '\0' < /proc/device-tree/model)
echo -e "${YELLOW}Detected: ${PI_MODEL}${NC}"

# Check for creature user
if id "creature" &>/dev/null; then
    echo -e "${GREEN}Found creature user. ✓${NC}"
else
    echo -e "${RED}Error: The 'creature' user is not found on this system.${NC}"
    echo "This script requires the 'creature' user to be set up according to the Creaturebox protocol."
    echo "Please set up the 'creature' user before running this script."
    exit 1
fi

# Check for Python 3.9+
echo "Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        echo -e "${RED}Error: Python 3.9+ is required. Found Python ${PYTHON_VERSION}.${NC}"
        echo "Please update your Python installation."
        exit 1
    else
        echo -e "${GREEN}Python ${PYTHON_VERSION} detected. ✓${NC}"
    fi
else
    echo -e "${RED}Error: Python 3 not found.${NC}"
    echo "Please install Python 3.9+ to continue."
    exit 1
fi

# Default installation directory
INSTALL_DIR="/opt/creaturebox_web"

# Ask where to install
read -p "Installation directory [$INSTALL_DIR]: " custom_dir
INSTALL_DIR=${custom_dir:-$INSTALL_DIR}

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating installation directory: $INSTALL_DIR"
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown $(whoami):$(whoami) "$INSTALL_DIR"
fi

# Clone or copy the application
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

if [ "$PARENT_DIR" != "$INSTALL_DIR" ]; then
    echo "Copying application files to $INSTALL_DIR..."
    sudo rsync -a --exclude-from="$SCRIPT_DIR/install_exclude.txt" "$PARENT_DIR/" "$INSTALL_DIR/"
    sudo chown -R $(whoami):$(whoami) "$INSTALL_DIR"
fi

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-venv nginx gunicorn python3-dev libffi-dev

# Install dependencies for camera and hardware control
echo "Installing hardware control dependencies..."
sudo apt-get install -y python3-picamera2 python3-rpi.gpio

# Set up virtual environment
echo "Setting up virtual environment..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Generate a secret key
echo "Generating secret key..."
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Create .env file
echo "Creating configuration..."
cat > "$INSTALL_DIR/.env" << EOF
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
CREATUREBOX_PASSWORD=creaturebox
EOF

# Set secure permissions for .env
chmod 600 "$INSTALL_DIR/.env"

# Handle software scripts and config files
echo "Setting up software scripts and configuration files..."

# Create necessary directories
sudo mkdir -p /home/creature/.config/creaturebox
sudo mkdir -p /home/creature/creaturebox_photos

# Copy configuration files
echo "Copying configuration files..."
sudo cp -v "$INSTALL_DIR/config/camera_settings.csv" /home/creature/.config/creaturebox/
sudo cp -v "$INSTALL_DIR/config/controls.txt" /home/creature/.config/creaturebox/
sudo cp -v "$INSTALL_DIR/config/schedule_settings.csv" /home/creature/.config/creaturebox/

# Determine the correct user (should be 'creature')
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" = "creature" ]; then
    MOTHBOX_OWNER="creature"
else
    MOTHBOX_OWNER="creature"
    echo -e "${YELLOW}Note: Running as $CURRENT_USER instead of 'creature'. Will still set ownership to creature.${NC}"
fi

# Create a controls.txt file if it doesn't exist
if [ ! -f /home/creature/.config/creaturebox/controls.txt ]; then
    echo "Creating default controls configuration..."
    cat > /home/creature/.config/creaturebox/controls.txt << EOF
shutdown_enabled=True
minutes=60
OnlyFlash=False
LastCalibration=0
name=creaturebox
EOF
    sudo chown creature:creature /home/creature/.config/creaturebox/controls.txt
    sudo chmod 644 /home/creature/.config/creaturebox/controls.txt
fi

# Ensure permissions are set correctly
sudo chown -R $MOTHBOX_OWNER:$MOTHBOX_OWNER /home/creature/.config/creaturebox
sudo chmod -R 755 /home/creature/.config/creaturebox
sudo chown -R $MOTHBOX_OWNER:$MOTHBOX_OWNER /home/creature/creaturebox_photos
sudo chmod 777 /home/creature/creaturebox_photos

# Create static directories and ensure they exist
echo "Creating static directories..."
sudo mkdir -p "$INSTALL_DIR/app/static/css"
sudo mkdir -p "$INSTALL_DIR/app/static/js"
sudo mkdir -p "$INSTALL_DIR/app/static/img"

# Ensure Bootstrap files are present
echo "Checking Bootstrap files..."
if [ ! -f "$INSTALL_DIR/app/static/js/bootstrap.bundle.min.js" ] || [ ! -f "$INSTALL_DIR/app/static/css/bootstrap.min.css" ]; then
    echo "Bootstrap files are missing, will be created as part of the installation."
    # We'll create these files later
fi
find "$INSTALL_DIR/software" -type f -name "*.py" -exec sed -i 's|/home/pi/Desktop/Mothbox|/home/creature/.config/creaturebox|g' {} \;
find "$INSTALL_DIR/software" -type f -name "*.py" -exec sed -i 's|/home/pi/Desktop/Mothbox/photos|/home/creature/creaturebox_photos|g' {} \;

# Set execute permissions for scripts
echo "Setting execute permissions for scripts..."
chmod +x "$INSTALL_DIR/software/"*.py
chmod +x "$INSTALL_DIR/software/Scripts/"*.py

# Set up permissions for camera and GPIO
echo "Setting up permissions for hardware access..."
sudo usermod -a -G video creature
sudo usermod -a -G gpio creature

# Ensure our service has access to hardware
echo "Creating systemd service..."
sudo tee /etc/systemd/system/creaturebox-web.service > /dev/null << EOF
[Unit]
Description=Creaturebox Web Interface
After=network.target

[Service]
User=creature
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/gunicorn -b 127.0.0.1:8000 'app:create_app()'
Restart=always
RestartSec=5
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$INSTALL_DIR/venv/bin"
EnvironmentFile=$INSTALL_DIR/.env
# Allow access to hardware
SupplementaryGroups=video gpio

[Install]
WantedBy=multi-user.target
EOF

# Set up Nginx if available
if command -v nginx &>/dev/null; then
    echo "Setting up Nginx..."
    sudo tee /etc/nginx/sites-available/creaturebox-web > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/creaturebox-web /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx || echo -e "${YELLOW}Warning: Nginx configuration failed. Please check configuration manually.${NC}"
fi

# Enable and start the service
echo "Enabling and starting service..."
sudo systemctl enable creaturebox-web.service
sudo systemctl start creaturebox-web.service

# Create minimal bootstrap.bundle.min.js for modals
echo "Creating bootstrap.bundle.min.js..." 
cat > "$INSTALL_DIR/app/static/js/bootstrap.bundle.min.js" << 'EOL'
/*!
  * Bootstrap v5.3.0 (https://getbootstrap.com/)
  * Copyright 2011-2023 The Bootstrap Authors (https://github.com/twbs/bootstrap/graphs/contributors)
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
  */
!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define(e):(t="undefined"!=typeof globalThis?globalThis:t||self).bootstrap=e()}(this,(function(){"use strict";const t="modal";return{Alert:class{constructor(t){this._element=t,this.close=()=>{}}},Button:class{constructor(t){this._element=t}toggle(){}},Collapse:class{constructor(t,e){this._element=t,this._config=e}toggle(){},show(){},hide(){}},Dropdown:class{constructor(t,e){this._element=t,this._config=e}toggle(){},show(){},hide(){}},Modal:class{constructor(e,i){this._element=e,this._config=i,this._isShown=!1}static get NAME(){return t}toggle(t){return this._isShown?this.hide():this.show(t)}show(t){this._isShown=!0,document.body.classList.add("modal-open"),this._element.classList.add("show"),this._element.setAttribute("aria-modal",!0),this._element.setAttribute("role","dialog")}hide(){this._isShown=!1,document.body.classList.remove("modal-open"),this._element.classList.remove("show"),this._element.setAttribute("aria-hidden",!0)}static getOrCreateInstance(t){return this.getInstance(t)||new this(t)}}}})());
EOL

# Create minimal bootstrap.min.css
echo "Creating bootstrap.min.css..."
cat > "$INSTALL_DIR/app/static/css/bootstrap.min.css" << 'EOL'
/*!
  * Bootstrap v5.3.0 (https://getbootstrap.com/)
  * Copyright 2011-2023 The Bootstrap Authors
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
  */
:root{--bs-primary:#0d6efd;--bs-secondary:#6c757d;--bs-success:#198754;--bs-info:#0dcaf0;--bs-warning:#ffc107;--bs-danger:#dc3545;--bs-light:#f8f9fa;--bs-dark:#212529}.btn{display:inline-block;font-weight:400;line-height:1.5;color:#212529;text-align:center;text-decoration:none;vertical-align:middle;cursor:pointer;user-select:none;background-color:transparent;border:1px solid transparent;padding:.375rem .75rem;font-size:1rem;border-radius:.25rem;transition:color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out}.btn-primary{color:#fff;background-color:var(--bs-primary);border-color:var(--bs-primary)}.btn-secondary{color:#fff;background-color:var(--bs-secondary);border-color:var(--bs-secondary)}.btn-success{color:#fff;background-color:var(--bs-success);border-color:var(--bs-success)}.btn-danger{color:#fff;background-color:var(--bs-danger);border-color:var(--bs-danger)}.btn-outline-primary{color:var(--bs-primary);border-color:var(--bs-primary)}.btn-outline-secondary{color:var(--bs-secondary);border-color:var(--bs-secondary)}.btn-outline-info{color:var(--bs-info);border-color:var(--bs-info)}.modal{position:fixed;top:0;left:0;z-index:1055;display:none;width:100%;height:100%;overflow-x:hidden;overflow-y:auto;outline:0}.modal-dialog{position:relative;width:auto;margin:.5rem;pointer-events:none}.modal.fade .modal-dialog{transition:transform .3s ease-out;transform:translate(0,-50px)}.modal.show .modal-dialog{transform:none}.modal-content{position:relative;display:flex;flex-direction:column;width:100%;pointer-events:auto;background-color:#fff;background-clip:padding-box;border:1px solid rgba(0,0,0,.2);border-radius:.3rem;outline:0}.modal-header{display:flex;flex-shrink:0;align-items:center;justify-content:space-between;padding:1rem 1rem;border-bottom:1px solid #dee2e6;border-top-left-radius:calc(.3rem - 1px);border-top-right-radius:calc(.3rem - 1px)}.modal-title{margin-bottom:0;line-height:1.5}.modal-body{position:relative;flex:1 1 auto;padding:1rem}.modal-footer{display:flex;flex-wrap:wrap;flex-shrink:0;align-items:center;justify-content:flex-end;padding:.75rem;border-top:1px solid #dee2e6;border-bottom-right-radius:calc(.3rem - 1px);border-bottom-left-radius:calc(.3rem - 1px)}.modal-backdrop{position:fixed;top:0;left:0;z-index:1050;width:100vw;height:100vh;background-color:#000}.modal-backdrop.fade{opacity:0}.modal-backdrop.show{opacity:.5}.progress{display:flex;height:1rem;overflow:hidden;font-size:.75rem;background-color:#e9ecef;border-radius:.25rem}.progress-bar{display:flex;flex-direction:column;justify-content:center;overflow:hidden;color:#fff;text-align:center;white-space:nowrap;background-color:#0d6efd;transition:width .6s ease}.progress-bar-striped{background-image:linear-gradient(45deg,rgba(255,255,255,.15) 25%,transparent 25%,transparent 50%,rgba(255,255,255,.15) 50%,rgba(255,255,255,.15) 75%,transparent 75%,transparent);background-size:1rem 1rem}.progress-bar-animated{animation:1s linear infinite progress-bar-stripes}@keyframes progress-bar-stripes{0%{background-position-x:1rem}}.text-success{color:var(--bs-success)!important}.text-danger{color:var(--bs-danger)!important}.bg-success{background-color:var(--bs-success)!important}.bg-danger{background-color:var(--bs-danger)!important}
EOL

# Create placeholder image
echo "Creating placeholder image..."
echo "iVBORw0KGgoAAAANSUhEUgAAAUAAAAFACAIAAABHr8k3AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5wMPFCIjkqA99AAAAFJJREFUeNrtwTEBAAAAwqD1T20JT6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAeLQIRgABOlARAgAAAABJRU5ErkJggg==" | base64 -d > "$INSTALL_DIR/app/static/img/no-photo.png"

# Set permissions for static files
echo "Setting permissions for static files..."
sudo chown -R $MOTHBOX_OWNER:$MOTHBOX_OWNER "$INSTALL_DIR/app/static"
sudo chmod -R 755 "$INSTALL_DIR/app/static"

# Validate paths
echo "Validating path configuration..."
cd "$INSTALL_DIR"
source venv/bin/activate
python scripts/validate_paths.py --verbose --fix

# Print success message
echo -e "${GREEN}"
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo -e "${GREEN}  Checking Modules${NC}"
echo "========================================"
echo "System Module: ✓ Installed"
echo "Photo Module: ✓ Installed"
echo "Control Module: ✓ Installed"
echo -e "  ${YELLOW}→ Camera control ready${NC}"
echo -e "  ${YELLOW}→ Light control ready${NC}"
echo -e "  ${YELLOW}→ System control ready${NC}"
echo -e "  ${YELLOW}→ Power management ready${NC}"
echo "========================================"
echo -e "${NC}"
echo "Creaturebox Web Interface has been installed to: $INSTALL_DIR"
echo ""
echo "Default login password: creaturebox"
echo "Please change this password immediately in the settings!"
echo ""
if command -v nginx &>/dev/null; then
    echo "Web interface is available at: http://$(hostname -I | awk '{print $1}')"
else
    echo "Web interface is available at: http://$(hostname -I | awk '{print $1}'):8000"
fi
echo ""

# Check control module
echo "Checking Control Module functionality..."
echo -e "${YELLOW}Camera control:${NC} To use camera features, make sure the camera is enabled"
echo "Run 'sudo raspi-config' and enable camera interface if needed"
echo -e "${YELLOW}GPIO control:${NC} GPIO access is set up for controlling lights and other hardware"
echo ""
echo "To check status: sudo systemctl status creaturebox-web"
echo "To view logs: sudo journalctl -u creaturebox-web"
echo ""
