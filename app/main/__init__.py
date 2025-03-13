"""
Main blueprint for the Creaturebox Web Interface.

This blueprint handles the main routes and views for the application.
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
