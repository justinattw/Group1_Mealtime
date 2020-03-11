from flask_wtf import FlaskForm
from sqlalchemy import or_
from wtforms import StringField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length

from app import db
from app.models import Users, UserAllergies, UserDietPreferences

# GLOBAL VARIABLES
MIN_PW_LEN = 6
MAX_PW_LEN = 20

DIET_CHOICES = [(1, 'Classic'),
                (2, 'Pescatarian'),
                (3, 'Vegetarian'),
                (4, 'Vegan')]

ALLERGY_CHOICES = [(1, 'Dairy-free'),
                   (2, 'Gluten-free'),
                   (3, 'Seafood-free'),
                   (4, 'Eggs-free'),
                   (5, 'Lupin-free'),
                   (6, 'Mustard-free'),
                   (7, 'Tree nuts-free'),
                   (8, 'Peanuts-free'),
                   (9, 'Sesame-free'),
                   (10, 'Soybeans-free'),
                   (11, 'Celery-free')]


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
        results = db.session.query(Users).filter(Users.email == email.data).first()
        if results is not None:
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


class EditPreferencesForm(FlaskForm):
    diet_type = SelectField('Diet type', choices=DIET_CHOICES)
    allergies = SelectMultipleField(u'Allergies (shift+click to select multiple)', choices=ALLERGY_CHOICES)
