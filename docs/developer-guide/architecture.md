# Architecture

This document provides an overview of the Creaturebox Web Interface architecture and design patterns.

## Overview

The Creaturebox Web Interface is built using Flask, a lightweight WSGI web application framework in Python. The application follows a modular blueprint-based architecture to support future expansion and maintainability.

## Directory Structure

```
creaturebox_web/
├── app/                    # Main application package
│   ├── __init__.py         # Application factory
│   ├── auth/               # Authentication module
│   │   ├── __init__.py     # Blueprint definition
│   │   ├── decorators.py   # Auth decorators
│   │   ├── forms.py        # Form definitions
│   │   └── routes.py       # Auth routes
│   ├── main/               # Main module
│   │   ├── __init__.py     # Blueprint definition
│   │   └── routes.py       # Main routes
│   ├── static/             # Static assets
│   │   ├── css/            # CSS stylesheets
│   │   ├── js/             # JavaScript files
│   │   └── img/            # Images
│   ├── templates/          # Jinja2 templates
│   │   ├── auth/           # Auth templates
│   │   ├── main/           # Main templates
│   │   └── base.html       # Base template
│   └── utils/              # Utility functions
│       └── security.py     # Security utilities
├── config/                 # Configuration
│   └── default.py          # Default configuration
├── docs/                   # Documentation
├── scripts/                # Installation scripts
├── .env                    # Environment variables (not in repo)
├── requirements.txt        # Python dependencies
├── run.py                  # Development server script
└── wsgi.py                 # WSGI entry point
```

## Application Factory Pattern

The application uses the Flask application factory pattern, which allows for creating multiple instances of the application, particularly useful for testing.

```python
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # Load configuration
    # Initialize extensions
    # Register blueprints
    return app
```

## Blueprints

The application is organized into blueprints, which are modular components:

- **Auth Blueprint**: Handles authentication and session management
- **Main Blueprint**: Provides the main interface and dashboard
- **Future Blueprints**: Will include photo, control, and settings modules

## Authentication

Authentication uses a single-password approach with session management. Sessions are stored server-side for security, and CSRF protection is implemented for all forms.

## Frontend Architecture

The frontend uses a custom CSS framework with a responsive design:

- **Dark Theme**: Using green, purple, and white highlights
- **Responsive Design**: Adapting to different screen sizes
- **Component-Based**: Reusable UI components for cards, buttons, etc.

## Extension Points

The architecture is designed with extension points for future modules:

1. **New Blueprints**: Add new functionality by creating additional blueprints
2. **Template Inheritance**: Extend base templates for consistent UI
3. **Utility Functions**: Common utilities can be shared across modules

## Integration Layer

The application interacts with the existing Creaturebox/Mothbox software through an integration layer:

- **Subprocess Handling**: Running external scripts
- **Configuration Mapping**: Reading and writing to configuration files
- **Hardware Abstraction**: Interfacing with camera and control systems

## Security Considerations

Security measures implemented in the architecture:

- **CSRF Protection**: All forms are protected against cross-site request forgery
- **Session Management**: Server-side sessions with secure cookies
- **Password Security**: Passwords are stored using secure hashing
- **Rate Limiting**: Prevents brute force attacks on login
- **HTTP Headers**: Security headers to prevent common web vulnerabilities

## Deployment Architecture

For production deployment, the application uses:

- **Gunicorn**: WSGI HTTP Server
- **Nginx**: Reverse proxy and static file serving
- **Systemd**: Service management

## Future Architecture Considerations

As the application evolves, these architectural components are planned:

- **Photo Processing Pipeline**: Handling image uploads, thumbnails, and organization
- **Hardware Control Interface**: Direct control of camera and lighting hardware
- **Settings Management**: Configuration file parsing and validation
- **Monitoring System**: Health checks and system monitoring
