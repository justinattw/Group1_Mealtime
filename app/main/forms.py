#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/main/forms.py:

This document includes WTForms for authentication methods.
Authentication methods include signup, login, edit account details and log out.
"""
__authors__ = "Ethan Low, Danny Wallis, and Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, HiddenField
from wtforms.fields.html5 import IntegerRangeField, IntegerField
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

    # Set field to render slider current values
    amount = StringField()

    # Field for calorie range
    hidden = HiddenField()

    allergies = SelectMultipleField('Allergies (cmd/ctrl + click to select multiple)', choices=ALLERGY_CHOICES)
