"""
Authentication routes for the Creaturebox Web Interface.
"""

from flask import render_template, redirect, url_for, request, session, flash, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth import bp
from app.auth.forms import LoginForm
from app.auth.decorators import login_required
from app.utils.security import get_password_hash
from app import limiter

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Handle user login."""
    if 'authenticated' in session and session['authenticated']:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        stored_password = current_app.config['CREATUREBOX_PASSWORD']
        
        # For first time setup, we use plaintext comparison
        # In production, we'll use the hashed password
        if 'password_hash' in current_app.config:
            is_valid = check_password_hash(current_app.config['password_hash'], password)
        else:
            is_valid = (password == stored_password)
            
            # If using plaintext, hash it for future use
            if is_valid:
                current_app.config['password_hash'] = generate_password_hash(stored_password)
        
        if is_valid:
            session['authenticated'] = True
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Invalid password', 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    """Log the user out."""
    session.pop('authenticated', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
