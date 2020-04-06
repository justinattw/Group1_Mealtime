#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/auth/main_functions.py:

This document includes functions that assists the main routes.
"""
__authors__ = "Danny Wallis and Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import db
from app.models import Recipes, RecipeAllergies, RecipeDietTypes, NutritionValues, MealPlans

from flask import flash, render_template, request, redirect, url_for
from flask_login import current_user
from functools import wraps
from sqlalchemy import and_
from sqlalchemy.sql import func


def search_function(search_term="", diet_type=1, allergy_list=[], min_cal=0, max_cal=1000, max_time=99999):
    """
    This function accepts 5 parameters to find appropriate recipes according to user input (or default values)

    The search function is used by view_all_recipes, a simple search, and advanced_search.

    :param search_term: search term for recipe name
    :param diet_type: specified diet type
    :param allergy_list: list of allergies
    :param min_cal: minimum calorie
    :param max_cal: maximum calorie
    :param max_time: maximum time that user wants to prep+cook for
    :return: an SQLAlchemy query of recipes matching the above parameters
    """
    # Subquery: blacklist recipes if user has certain allergies
    blacklist = db.session.query(RecipeAllergies.recipe_id) \
        .filter(RecipeAllergies.allergy_id.in_(allergy_list)).distinct().subquery()

    # Filter allergies with a left outer join on blacklist, so that blacklisted recipes are not matched
    results = db.session.query(Recipes) \
        .outerjoin(blacklist, Recipes.recipe_id == blacklist.c.recipe_id) \
        .filter(blacklist.c.recipe_id == None) \
        .join(RecipeDietTypes, Recipes.recipe_id == RecipeDietTypes.recipe_id) \
        .join(NutritionValues, Recipes.recipe_id == NutritionValues.recipe_id) \
        .filter(RecipeDietTypes.diet_type_id >= diet_type) \
        .filter(Recipes.recipe_name.contains(search_term)) \
        .filter(and_(NutritionValues.calories >= min_cal,
                     NutritionValues.calories <= max_cal)) \
        .filter(Recipes.total_time <= max_time)

    return results


def get_most_recent_mealplan_id():
    """
    Get the most recent mealplan for currently active user.

    :return: mealplan_id
    """
    # Get the most recent mealplan by taking max(mealplan_id)
    mealplan_id, = db.session.query(func.max(MealPlans.mealplan_id)) \
        .filter(MealPlans.user_id == current_user.id).first()

    return mealplan_id


# def check_user_owns_mealplan(func):
#     """
#     If you decorate this a view with this, it will ensure that the mealplan belongs to the current_user. This is to
#     protect users from being able to see other users' mealplans
#
#     :param mealplan_id:
#     :return:
#     """
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         mealplan_id = request.args.get('mealplan_id')
#
#         user_owns_mealplan = db.session.query(MealPlans) \
#             .filter(MealPlans.user_id == current_user.id) \
#             .filter(MealPlans.mealplan_id == mealplan_id) \
#             .first()
#         print(mealplan_id)
#
#         print(user_owns_mealplan)
#
#         if user_owns_mealplan:
#             return func(*args, **kwargs)
#         else:
#             flash('Sorry, you do not have access to this meal plan', 'warning')
#             return redirect(url_for('main.mealplans_history'))
#     return decorated_function



def check_user_owns_mealplan(mealplan_id):

    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            user_owns_mealplan = db.session.query(MealPlans) \
                .filter(MealPlans.user_id == current_user.id) \
                .filter(MealPlans.mealplan_id == mealplan_id) \
                .first()

            if user_owns_mealplan:
                return func(*args, **kwargs)
            else:
                flash('Sorry, you do not have access to this meal plan', 'warning')
                return redirect(url_for('main.mealplans_history'))

        return decorated_view
    return decorator