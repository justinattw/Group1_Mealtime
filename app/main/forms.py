from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, IntegerField, validators
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired

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


class CalorieSearch(FlaskForm):
    upper_callimit = IntegerRangeField('Adjust max calories per meal (in kcal)', default=1000)
    lower_callimit = IntegerRangeField('Adjust min calories per meal (in kcal)', default=0)
