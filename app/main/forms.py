#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/main/forms.py:

This document includes WTForms for authentication methods.
Authentication methods include signup, login, edit account details and log out.
"""
__authors__ = "Ethan Low, Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

import config

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, HiddenField

DIET_CHOICES = config.DIET_CHOICES
ALLERGY_CHOICES = config.ALLERGY_CHOICES


class AdvSearchRecipes(FlaskForm):
    """
    AdvSearchRecipes Form takes in different
    """
    search_term = StringField('Search')
    diet_type = SelectField('Diet type', choices=DIET_CHOICES)

    cals = HiddenField()  # Field for calorie range
    max_time = HiddenField()  # Field for max cooking time

    allergies = SelectMultipleField('Allergies (cmd/ctrl + click to select multiple)', choices=ALLERGY_CHOICES)
