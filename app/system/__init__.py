"""
System module for the Creaturebox Web Interface.

This blueprint handles system monitoring, log viewing, and system controls.
"""

from flask import Blueprint

bp = Blueprint('system', __name__)

from app.system import routes
