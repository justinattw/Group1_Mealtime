#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/auth/forms.py:

This document includes WTForms for authentication methods.
Authentication methods include signup, login, edit account details and log out.
"""
__authors__ = "Ethan Low, Danny Wallis, and Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"


from app import db
from app.models import Users, UserAllergies, UserDietPreferences
import config

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length

# GLOBAL VARIABLES taken from config file
MIN_PW_LEN = config.MIN_PW_LEN
MAX_PW_LEN = config.MAX_PW_LEN

DIET_CHOICES = config.DIET_CHOICES
ALLERGY_CHOICES = config.ALLERGY_CHOICES


class SignupForm(FlaskForm):
    """
    SignupForm requests user details
    """
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message='Valid email address required')])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=MIN_PW_LEN,
                                                max=MAX_PW_LEN,
                                                message=f'Password must be between {MIN_PW_LEN} and {MAX_PW_LEN} characters long.'),
                                         EqualTo('confirm', message='The passwords do not match')])
    confirm = PasswordField('Confirm Password')

    def validate_email(self, email):
        if db.session.query(Users).filter(Users.email == (email.data).lower()).first():
            raise ValidationError('An account is already registered with this email.')


class LoginForm(FlaskForm):
    """
    LoginForm
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')


class EditPasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(),
                                                             Length(min=MIN_PW_LEN,
                                                                    max=MAX_PW_LEN,
                                                                    message=f'Password must be between {MIN_PW_LEN} and {MAX_PW_LEN} characters long.'),
                                                             EqualTo('confirm_password',
                                                                     message='The passwords do not match.')])
    confirm_password = PasswordField('Confirm password')

    def validate_old_and_new_passwords_different(self, old_password, new_password):
        if old_password == new_password:
            raise ValidationError("You can't set your new password to the same password.")


class EditPreferencesForm(FlaskForm):
    diet_type = SelectField('Diet type', choices=DIET_CHOICES)
    allergies = SelectMultipleField(u'Allergies (ctrl+click to select multiple)', choices=ALLERGY_CHOICES)