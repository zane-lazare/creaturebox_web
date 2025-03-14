#!/bin/bash
# Run the path validation script using the virtual environment Python

# Set paths
INSTALL_DIR="/opt/creaturebox_web"
REPO_DIR="$HOME/creaturebox_web"
SCRIPT_NAME="validate_paths.py"

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creaturebox Web Interface - Path Validation Script${NC}"

# Check if we're in a production environment
if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/venv/bin/python" ]; then
    echo "Running validation in production environment..."
    
    # Activate virtual environment and run script
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # Check if script exists in installation directory
    if [ -f "$INSTALL_DIR/scripts/$SCRIPT_NAME" ]; then
        echo "Using script from installation directory..."
        python "$INSTALL_DIR/scripts/$SCRIPT_NAME" "$@"
    elif [ -f "$REPO_DIR/scripts/$SCRIPT_NAME" ]; then
        echo "Using script from repository..."
        python "$REPO_DIR/scripts/$SCRIPT_NAME" "$@"
    else
        echo -e "${RED}Error: Could not find validation script.${NC}"
        exit 1
    fi
# Check if we're in development environment
elif [ -d "$REPO_DIR" ]; then
    echo "Running validation in development environment..."
    cd "$REPO_DIR"
    
    # Check if Python is available
    if command -v python &> /dev/null; then
        python "scripts/$SCRIPT_NAME" "$@"
    else
        echo -e "${RED}Error: Python not found.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Neither production nor development environment found.${NC}"
    exit 1
fi
