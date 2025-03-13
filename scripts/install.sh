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

# Create systemd service file
echo "Setting up systemd service..."
sudo tee /etc/systemd/system/creaturebox-web.service > /dev/null << EOF
[Unit]
Description=Creaturebox Web Interface
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/gunicorn -b 127.0.0.1:8000 'app:create_app()'
Restart=always
RestartSec=5
Environment="PATH=$INSTALL_DIR/venv/bin"
EnvironmentFile=$INSTALL_DIR/.env

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

# Print success message
echo -e "${GREEN}"
echo "========================================"
echo "  Installation Complete!"
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
echo "To check status: sudo systemctl status creaturebox-web"
echo "To view logs: sudo journalctl -u creaturebox-web"
echo ""
