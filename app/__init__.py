"""
Creaturebox Web Interface - Flask Application Package

This package contains the main Flask application for the Creaturebox Web Interface.
"""

import os
import logging
import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["3600 per hour"]
)

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'creaturebox.sqlite'),
        CREATUREBOX_PASSWORD=os.environ.get('CREATUREBOX_PASSWORD', 'creaturebox'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB max upload size
        BASE_DIR=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # Add base directory for script execution
    )
    
    # Load test config if passed in
    if test_config is not None:
        app.config.from_mapping(test_config)
    # Load the instance config, if it exists
    else:
        app.config.from_pyfile('config.py', silent=True)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with the app
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.system import bp as system_bp
    app.register_blueprint(system_bp, url_prefix='/system')
    
    from app.photos import bp as photos_bp
    app.register_blueprint(photos_bp, url_prefix='/photos')
    
    # Initialize control module
    from app.control import init_app as init_control
    init_control(app)
    
    # Set up logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/creaturebox.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Creaturebox Web Interface startup')
    
    # Add context processors for template variables
    @app.context_processor
    def inject_now():
        """Make the current datetime available to all templates as 'now'."""
        return {'now': datetime.datetime.now()}
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app
