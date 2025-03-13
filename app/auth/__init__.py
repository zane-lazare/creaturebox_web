"""
Authentication blueprint for the Creaturebox Web Interface.

This blueprint handles authentication-related routes and functionality.
"""

from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth import routes
