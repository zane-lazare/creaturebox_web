#!/bin/bash
# Script to fix Bootstrap dependency issues
# Run this script on the Raspberry Pi after deploying the code

# Set directory paths
DEPLOY_DIR="/opt/creaturebox_web"
STATIC_DIR="$DEPLOY_DIR/app/static"

# Create directories if they don't exist
mkdir -p "$STATIC_DIR/js"
mkdir -p "$STATIC_DIR/css"
mkdir -p "$STATIC_DIR/img"

# Copy Bootstrap files
echo "Copying Bootstrap files..."

# Copy JavaScript
sudo cp $STATIC_DIR/js/bootstrap.bundle.min.js $STATIC_DIR/js/bootstrap.bundle.min.js.backup 2>/dev/null || true
sudo cp $HOME/creaturebox_web/app/static/js/bootstrap.bundle.min.js $STATIC_DIR/js/

# Copy CSS
sudo cp $STATIC_DIR/css/bootstrap.min.css $STATIC_DIR/css/bootstrap.min.css.backup 2>/dev/null || true
sudo cp $HOME/creaturebox_web/app/static/css/bootstrap.min.css $STATIC_DIR/css/

# Copy image
sudo cp $STATIC_DIR/img/no-photo.png $STATIC_DIR/img/no-photo.png.backup 2>/dev/null || true
sudo cp $HOME/creaturebox_web/app/static/img/no-photo.png $STATIC_DIR/img/

# Set permissions
sudo chown -R www-data:www-data $STATIC_DIR
sudo chmod -R 755 $STATIC_DIR

# Restart web service
sudo systemctl restart creaturebox-web

echo "Bootstrap fix completed!"
echo "Please refresh your browser and try the camera controls again."
