"""
Default configuration for the Creaturebox Web Interface.
"""

import os
from datetime import timedelta

# Base directory for the application
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Secret key for session encryption
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')

# Default password for authentication
CREATUREBOX_PASSWORD = os.environ.get('CREATUREBOX_PASSWORD', 'creaturebox')

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(BASE_DIR, 'sessions')
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Logging configuration
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(LOG_DIR, 'creaturebox.log')
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# System paths
SYSTEM_PATHS = {
    'config': '/path/to/creaturebox/config',
    'data': '/path/to/creaturebox/data',
    'logs': '/path/to/creaturebox/logs',
    'photos': '/path/to/creaturebox/photos',
}

# Upload configurations
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'}

# Theme configuration
THEME = {
    'name': 'default',
    'dark_mode': True,
    'primary_color': '#57bb8a',  # Green
    'secondary_color': '#b267e6',  # Purple
    'text_color': '#ffffff',  # White
    'background_color': '#121212',  # Dark
}
