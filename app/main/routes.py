"""
Main routes for the Creaturebox Web Interface.
"""

from flask import render_template, current_app
from app.main import bp
from app.auth.decorators import login_required

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Render the main dashboard page."""
    return render_template('main/index.html', title='Dashboard')

@bp.route('/about')
@login_required
def about():
    """Render the about page."""
    return render_template('main/about.html', title='About')
