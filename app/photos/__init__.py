"""
Photos module for the Creaturebox Web Interface.

This blueprint handles photo browsing, viewing, and management.
"""

from flask import Blueprint

bp = Blueprint('photos', __name__)

from app.photos import routes
