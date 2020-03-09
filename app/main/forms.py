from flask_wtf import FlaskForm
from sqlalchemy import or_
from sqlalchemy.orm import with_polymorphic
from wtforms import StringField, PasswordField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from app import db
# from app.models import Student, User, Teacher
from app.models import Recipes, RecipeDietTypes, RecipeAllergies

DIET_CHOICES = [('classic', 'Classic'),
                ('pescatarian', 'Pescatarian'),
                ('vegetarian', 'Vegetarian'),
                ('vegan', 'Vegan')]

class AdvSearchRecipes(FlaskForm):
    search_term = StringField('Search')
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