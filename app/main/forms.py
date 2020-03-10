from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, IntegerField

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
    upper_callimit = IntegerField('Enter max calories per meal (in kcal)')
    lower_callimit = IntegerField('Enter min calories per meal (in kcal)')