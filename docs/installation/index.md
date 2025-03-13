# Installation Guide

This guide walks you through installing the Creaturebox Web Interface on your Raspberry Pi.

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS (Bullseye or newer)
- Python 3.9 or higher
- Internet connection for downloading dependencies
- Basic knowledge of terminal commands

## Installation Methods

There are two ways to install the Creaturebox Web Interface:

1. **Automated Installation (Recommended)**: Using the installation script
2. **Manual Installation**: Step-by-step installation process

## Automated Installation

The automated installation script will set up everything you need with minimal effort.

1. Download the installation files (either via Git or direct download)
2. Navigate to the downloaded directory
3. Run the installation script:

```bash
chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

4. Follow the prompts to complete the installation
5. Access the web interface using your Raspberry Pi's IP address

## Manual Installation

If you prefer to install manually or the automated script doesn't work for your setup, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/creaturebox_web.git
cd creaturebox_web
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the requirements:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
echo "FLASK_APP=app" > .env
echo "FLASK_ENV=production" >> .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env
echo "CREATUREBOX_PASSWORD=creaturebox" >> .env
```

5. Set up Gunicorn and Nginx:
```bash
# Gunicorn service file
sudo nano /etc/systemd/system/creaturebox-web.service
```

Add the following content (adjust paths as needed):
```
[Unit]
Description=Creaturebox Web Interface
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/creaturebox_web
ExecStart=/path/to/creaturebox_web/venv/bin/gunicorn -b 127.0.0.1:8000 'app:create_app()'
Restart=always
RestartSec=5
Environment="PATH=/path/to/creaturebox_web/venv/bin"
EnvironmentFile=/path/to/creaturebox_web/.env

[Install]
WantedBy=multi-user.target
```

6. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/creaturebox-web
```

Add the following content:
```
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

7. Enable the Nginx configuration:
```bash
sudo ln -sf /etc/nginx/sites-available/creaturebox-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

8. Start and enable the Gunicorn service:
```bash
sudo systemctl enable creaturebox-web.service
sudo systemctl start creaturebox-web.service
```

9. Access the web interface using your Raspberry Pi's IP address

## Post-Installation

After installation:

1. Change the default password immediately (login with "creaturebox" and go to Settings)
2. Configure your system paths in the settings
3. Set up any scheduled tasks or camera settings

## Troubleshooting

If you encounter issues with the installation:

- Check the logs: `sudo journalctl -u creaturebox-web`
- Verify the service is running: `sudo systemctl status creaturebox-web`
- Check for proper permissions on directories
- Ensure Python 3.9+ is installed: `python3 --version`

For more detailed troubleshooting, see the [Troubleshooting Guide](../troubleshooting.md).
