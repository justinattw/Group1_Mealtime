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


class AdvSearchRecipes(FlaskForm):
    search_term = StringField('Search')
    diet_type = SelectField('Diet type', choices=DIET_CHOICES)
    celery = BooleanField('Celery')
    gluten = BooleanField('Gluten')
    seafood = BooleanField('Seafood')
    eggs = BooleanField('Eggs')
    lupin = BooleanField('Lupin')
    mustard = BooleanField('Mustard')
    tree_nuts = BooleanField('Tree nuts')
    peanuts = BooleanField('Peanuts')
    sesame_seeds = BooleanField('Sesame seeds')
    soybeans = BooleanField('Soybeans')
    sulphur = BooleanField('Sulphur and sulphites')