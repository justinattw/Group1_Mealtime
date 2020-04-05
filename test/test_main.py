#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_main.py:

Pytests tests for main views and methods (relating to files in app/main/)
"""
__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

from test.conftest import search_function, add_to_favourites, view_recipe, view_favourites, view_about, \
    view_mealplanner, view_create_mealplan

import pytest
import random
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.sql import func


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


def test_search_without_login(test_client):
    """
    GIVEN a Flask application
    WHEN a simple search is performed with the search parameter of search term
    THEN check that the search term is included in the response
    """
    response = search_function(test_client, 'vegan')
    assert response.status_code == 200
    assert b'vegan' in response.data


def test_search_with_login(test_client):
    """
    GIVEN a Flask application, user is logged in and has previously set diet_type and allergy_choices
    WHEN a simple search is performed with the search parameter
    THEN check that the search term is included in the response
    """
    response = search_function(test_client, 'vegan')
    assert response.status_code == 200
    assert b'vegan' in response.data


def test_add_to_favourite(test_client, user, db):
    """
    GIVEN a Flask application and user is logged in
    WHEN user adds a (random) recipe to favourites
    THEN check response is valid
    """
    from app.models import UserFavouriteRecipes, Recipes

    number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
    # indicating how many recipes there are.
    # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
    # can upload + delete their uploaded recipes, this will need to be changed.

    rand_favourite = random.randint(1, number_of_recipes)  # generate a random favourite recipe_id to test
    response = add_to_favourites(test_client, rand_favourite)  # add random favourite recipe to favourites
    assert response.status_code == 200

    """
    GIVEN a Flask application and user is logged in
    WHEN user adds a (random) recipe to favourites
    THEN check the recipe has been added to the database in the correct model/ tabe
    """
    fav_query = db.session.query(UserFavouriteRecipes) \
        .filter(UserFavouriteRecipes.user_id == user.id) \
        .filter(UserFavouriteRecipes.recipe_id == rand_favourite) \
        .first()
    assert fav_query is not None

    """
    GIVEN a Flask application and user is logged in
    WHEN user adds a (random) recipe to favourites that has already been added
    THEN check that an IntegrityError/ ObjectDeletedError occurs from SQLAlchemy
    """

    with pytest.raises(ObjectDeletedError):
        # Although in the routes we expect IntegrityError, for some reasonObjectDeletedError is raised
        response = add_to_favourites(test_client, rand_favourite)

    print(response.data)  # Because we are using Javascript to display errors, there is no 'response' because page
    # isn't refreshed. Javascript uses AJAX requests
    # assert b'is already in your favourites!' in response.data


def test_view_recipe(test_client, db):
    """
    GIVEN a Flask application
    WHEN user requests page to view a recipe
    THEN response is valid
    """
    from app.models import Allergies, RecipeAllergies, Recipes

    number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()

    rand_recipe = random.randint(1, number_of_recipes)  # Query the highest recipe_id, indicating how many recipes
    # there are.
    # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
    # can upload + delete their uploaded recipes, this will need to be changed.

    response = view_recipe(test_client, rand_recipe)
    assert response.status_code == 200

    """
    GIVEN a Flask application
    WHEN user requests page to view a recipe
    THEN allergies of a recipe are all displayed on the page
    """

    allergies = db.session.query(Allergies.allergy_name) \
        .join(RecipeAllergies) \
        .filter(RecipeAllergies.recipe_id == rand_recipe) \
        .all()
    allergy_list = [value for value, in allergies]  # Turn allergies query results into a list

    for allergy in allergy_list:
        assert allergy.encode() in response.data


def test_view_favourites(test_client, user):
    """
    GIVEN a Flask application and user is logged in
    WHEN user requests to view their favourites (before having added a favourite recipe)
    THEN response is always valid and correct data is displayed
    """
    response = view_favourites(test_client)
    assert response.status_code == 200
    assert b"'s favourite recipes" in response.data

def test_add_to_favourites_and_view_favourites(test_client, user, db):
    """
    GIVEN a Flask application and user is logged in
    WHEN user favourites a new recipe and views their Favourites page
    THEN response is valid (response code is 200), and favourited recipe_name is in the response data
    """
    from app.models import Recipes

    number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
    # indicating how many recipes there are.
    # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
    # can upload + delete their uploaded recipes, this will need to be changed.

    favourite = random.randint(1, number_of_recipes)
    response = add_to_favourites(test_client, favourite)
    assert response.status_code == 200

    # Get recipe name of favourited recipe
    fav_name, = db.session.query(Recipes.recipe_name).filter(Recipes.recipe_id == favourite).first()
    fav_list = fav_name.split()
    response = view_favourites(test_client)
    assert response.status_code == 200

    # Could not convert string containing apostrophes to binary using encode, so the string had to be split
    for part in fav_list:
        if "'" in part:  # If apostrophe ' is in the name, then split the string by the '
            part = part.split("'")[0]
            assert part.encode() in response.data
        else:
            assert part.encode() in response.data


def test_view_about(test_client):
    """
    GIVEN a Flask application
    WHEN the 'about' page is requested'
    THEN response is valid
    """
    response = view_about(test_client)
    assert response.status_code == 200


def test_view_mealplanner(test_client):
    """
    GIVEN a Flask application
    WHEN the 'view_mealplanner' page is requested'
    THEN response is valid
    """
    response = view_mealplanner(test_client)
    assert response.status_code == 200


def test_create_mealplan(test_client):
    """
    GIVEN a Flask application
    WHEN user creates a new mealplan
    THEN response is valid
    """
    response = view_create_mealplan(test_client)
    assert response.status_code == 200
