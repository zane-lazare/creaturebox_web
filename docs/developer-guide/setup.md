# Development Setup Guide

This guide will help you set up a development environment for the Creaturebox Web Interface.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9 or higher
- Git
- A code editor (VSCode recommended)
- Basic knowledge of Flask, HTML, CSS, and JavaScript

## Setting Up the Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/creaturebox_web.git
cd creaturebox_web
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

# For development, you might want additional packages
pip install pytest pytest-flask flake8
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=dev-key-change-this-in-production
CREATUREBOX_PASSWORD=creaturebox
```

### 5. Run the Development Server

```bash
python run.py
```

The development server will start at http://localhost:5000.

## Development Workflow

### Code Organization

Follow these principles when adding code:

- **Blueprints**: New functionality should be organized into blueprints
- **Templates**: Use template inheritance from `base.html`
- **Static Files**: Place CSS in `static/css` and JS in `static/js`
- **Utilities**: Common functions go in the `utils` directory

### Adding New Routes

To add a new route:

1. Create or choose an appropriate blueprint
2. Add the route function in the blueprint's `routes.py`
3. Create a template in the blueprint's template directory
4. Register the blueprint in `app/__init__.py` if it's new

Example:

```python
@bp.route('/my-new-route')
@login_required
def my_new_route():
    return render_template('blueprint/my_template.html')
```

### Working with Forms

For forms:

1. Define the form class in the blueprint's `forms.py`
2. Create a template with the form
3. Handle form submission in the route function

### Adding Static Assets

When adding CSS or JavaScript:

1. Place the file in the appropriate static directory
2. Update the base template or specific template to include it
3. Use `url_for('static', filename='path/to/file')` in templates

### Testing Your Code

Run tests with:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_specific.py
```

## Common Development Tasks

### Adding a New Module

To add a new module (e.g., a Photo module):

1. Create a new directory in `app/` (e.g., `app/photo`)
2. Create blueprint files (`__init__.py`, `routes.py`, etc.)
3. Create templates in `app/templates/photo/`
4. Register the blueprint in `app/__init__.py`

### Modifying the Database Schema

If your module needs database storage:

1. Define models in a `models.py` file in your blueprint
2. Use Flask-SQLAlchemy for ORM
3. Create migrations using Flask-Migrate

### Working with the Existing Creaturebox Code

When integrating with existing code:

1. Use subprocess calls to run external scripts
2. Use file I/O to read/write configuration files
3. Create abstraction layers to simplify interactions

## Code Style and Guidelines

Follow these guidelines for consistent code:

### Python Code

- Follow PEP 8 style guide
- Use docstrings for all functions and classes
- Use type hints where appropriate
- Keep functions focused and small

### HTML/CSS/JavaScript

- Use consistent indentation (2 spaces recommended)
- Follow component-based design principles
- Keep JavaScript organized and modular
- Use CSS variables for consistent styling

### Git Workflow

- Create feature branches for new features
- Use descriptive commit messages
- Create pull requests for code review
- Keep commits focused and logical

## Documentation

Update documentation when you make changes:

1. Code comments and docstrings for Python code
2. Update MkDocs documentation in `docs/` directory
3. Build the documentation with `mkdocs build`
4. Preview documentation with `mkdocs serve`

## Building for Production

To create a production build:

1. Set environment variables to production values
2. Run the installation script
3. Test thoroughly before deployment

## Getting Help

If you need assistance with development:

- Check the existing documentation
- Review the source code for similar features
- Ask for clarification on specific requirements
