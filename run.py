#!/usr/bin/env python
"""
Development server script for Creaturebox Web Interface
Run this script to start the development server
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Set default environment variables for development
if not os.environ.get('FLASK_APP'):
    os.environ['FLASK_APP'] = 'app'
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-key-change-this-in-production'
if not os.environ.get('CREATUREBOX_PASSWORD'):
    os.environ['CREATUREBOX_PASSWORD'] = 'creaturebox'

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)