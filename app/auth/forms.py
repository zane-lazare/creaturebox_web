"""
Authentication forms for the Creaturebox Web Interface.
"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """Form for user login."""
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
