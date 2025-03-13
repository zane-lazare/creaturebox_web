# Creaturebox Web Interface Scripts

This directory contains scripts for installing, updating, and managing the Creaturebox Web Interface.

## Scripts

### install.sh
The installation script for setting up the Creaturebox Web Interface on a new system.

### uninstall.sh
The uninstallation script for removing the Creaturebox Web Interface from a system.

### update_deployment.sh
A script to update the deployed application files from the repository.

## Usage

### Updating the Deployment

To update an existing installation with the latest code from your repository:

1. Make sure your changes are committed and pushed to the repository
2. Run the update script:

```bash
cd ~/creaturebox_web/scripts
chmod +x update_deployment.sh
./update_deployment.sh
```

The script will:
- Pull the latest changes from the repository
- Create a backup of the current installation
- Update the installed files
- Restart the service
- Check the service status

If you encounter any issues, the script creates a backup that you can restore.
