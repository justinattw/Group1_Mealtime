from flask_wtf import FlaskForm
from sqlalchemy import or_
from sqlalchemy.orm import with_polymorphic
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from app import db
from app.models import Student, User, Teacher

DIET_CHOICES = [('classic', 'Classic'),
                ('vegetarian', 'Vegetarian'),
                ('pescatarian', 'Pescatarian'),
                ('vegan', 'Vegan')]

ALLERGY_CHOICES = [('', ''),
                   ('')]

class SearchRecipes(FlaskForm):
    search_term = StringField('Search')
    diet_type = SelectField('Diet type', choices=DIET_CHOICES)
    allergies =
