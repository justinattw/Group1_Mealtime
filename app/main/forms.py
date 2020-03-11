from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired

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


class AdvSearchRecipes(FlaskForm):
    """
    AdvSearchRecipes Form takes in different
    """
    search_term = StringField('Search')
    diet_type = SelectField('Diet type', choices=DIET_CHOICES)

    # Fields for upper and lower calorie limits
    upper_callimit = IntegerRangeField('Adjust max calories per meal (in kcal)', default=1000)
    lower_callimit = IntegerRangeField('Adjust min calories per meal (in kcal)', default=0)

    allergies = SelectMultipleField('Allergies (shift+click to select multiple)', choices=ALLERGY_CHOICES)
