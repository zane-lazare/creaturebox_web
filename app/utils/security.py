"""
Security utility functions for the Creaturebox Web Interface.
"""

import os
import secrets
from werkzeug.security import generate_password_hash

def get_random_string(length=32):
    """Generate a random string for use as a secret key."""
    return secrets.token_hex(length)

def get_password_hash(password):
    """Generate a password hash."""
    return generate_password_hash(password)

def generate_csrf_token():
    """Generate a CSRF token."""
    return secrets.token_hex(16)
