#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_main.py:

Pytests tests for main methods (relating to files in app/main/)
"""
import random
import string
import numpy as np
import pytest
import re
from sqlalchemy.orm.exc import ObjectDeletedError

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import config
from test.conftest import login_test_user, search_function, add_to_favourites, view_recipe, view_favourites, view_about, view_mealplanner, view_create_mealplan
regex = re.compile('[^a-zA-Z]')
def test_index_page_valid(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' home page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200


def test_index_content(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' home page is requested
    THEN check the response contains "Welcome!"
    """
    response = test_client.get('/')
    assert b'Meal planning made easy' in response.data


def test_search_function(test_client, user):
    response = search_function(test_client, 'veg')
    assert response.status_code == 200
    assert b'veg' in response.data


def test_add_to_favourite(test_client, user, db):
    from app.models import UserFavouriteRecipes
    login_test_user(test_client)
    favourite = np.random.randint(1, 1000)
    response = add_to_favourites(test_client, favourite)
    assert response.status_code == 204
    fav_query = db.session.query(UserFavouriteRecipes) \
        .filter(UserFavouriteRecipes.user_id == user.id) \
        .filter(UserFavouriteRecipes.recipe_id == favourite) \
        .first()

    assert fav_query is not None

    ###add the same recipe, assert Object Deleted Error
    with pytest.raises(ObjectDeletedError):
        response = add_to_favourites(test_client, favourite)
        # assert b'is already in your favourites!' in response.data


def test_view_recipe(test_client):
    from app.models import db, Allergies, RecipeAllergies
    recipe = np.random.randint(1, 1000)
    response = view_recipe(test_client, recipe)
    assert response.status_code==200

    allergies = db.session.query(Allergies.allergy_name) \
        .join(RecipeAllergies) \
        .filter(RecipeAllergies.recipe_id == recipe) \
        .all()
    allergy_list = [value for value, in allergies]  # Turn allergies query results into a list
    for allergy in allergy_list:
        assert allergy.encode() in response.data

def test_view_favourites(test_client, user, db):
    from app.models import UserFavouriteRecipes, Recipes
    login_test_user(test_client)
    response = view_favourites(test_client)
    assert response.status_code == 200
    favourite = 374 # np.random.randint(1, 1000)
    response = add_to_favourites(test_client, favourite)
    assert response.status_code==204
    fav_name, = db.session.query(Recipes.recipe_name) \
         .filter(Recipes.recipe_id == favourite).first()
    print(fav_name)
    fav_list = fav_name.split()
    response = view_favourites(test_client)
    assert response.status_code == 200
    ##### Could not successfully convert string containing apostraphes to binary, so the string had to be split
    for item in fav_list:
        if "'" in item:
            item = item.split("'")[0]
            print(item)
            assert item.encode() in response.data
        else:
            assert item.encode() in response.data

def test_view_about(test_client):
    response = view_about(test_client)
    assert response.status_code==200

def test_view_mealplanner(test_client):
    response = view_mealplanner(test_client)
    assert response.status_code==200

def test_view_create_mealplanner(test_client):
    response = view_create_mealplan(test_client)
    assert response.status_code==200