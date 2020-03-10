from flask_wtf import FlaskForm
from sqlalchemy import or_
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from app import db
from app.models import Users, UserAllergies, UserDietPreferences


class SignupForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message='Valid email address required')])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm', message='The passwords do not match')])
    confirm = PasswordField('Confirm Password')

    def validate_email(self, email):
        results = db.session.query(Users).filter(Users.email == email.data).first()
        if results is not None:
            raise ValidationError('An account is already registered with this email.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')


class EditPasswordForm(FlaskForm):

    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(),
                                                           EqualTo('confirm_password',
                                                                   message='The passwords do not match')])
    confirm_password = PasswordField('Confirm password')

class EditPreferencesForm(FlaskForm):



    DIET_CHOICES = [('classic', 'Classic'),
                    ('pescatarian', 'Pescatarian'),
                    ('vegetarian', 'Vegetarian'),
                    ('vegan', 'Vegan')]

    diet_type = SelectField('Diet type', choices=DIET_CHOICES)
    dairy = BooleanField('Dairy-free')
    celery = BooleanField('Celery-free')
    gluten = BooleanField('Gluten-free')
    seafood = BooleanField('Seafood-free')
    eggs = BooleanField('Eggs-free')
    lupin = BooleanField('Lupin-free')
    mustard = BooleanField('Mustard-free')
    tree_nuts = BooleanField('Tree nuts-free')
    peanuts = BooleanField('Peanuts-free')
    sesame = BooleanField('Sesame seeds-free')
    soybeans = BooleanField('Soybeans-free')