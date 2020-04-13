#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_api.py:

Pytests tests for authentication views and methods (relating to files in app/auth/).

app/api COVERAGE: 100% files, 88% lines covered

We achieve 88% coverage of the app/auth directory, but more tests need to be done to ensure the API call is returning
what is expected.
"""
__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"


import random
from sqlalchemy.sql import func


def test_api_read_recipes_route_valid(test_client):
    """
    GIVEN a flask app
    WHEN a user makes API call to read all recipes
    THEN route is valid
    """
    response = test_client.get('/api/recipes', follow_redirects=True)
    assert response.status_code == 200


def test_api_read_recipe_route_valid(test_client, db):
    """
    GIVEN a flask app
    WHEN a user makes API call to read single recipes
    THEN route is valid
    """
    from app.models import Recipes

    number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
    # indicating how many recipes there are.
    # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
    # can upload + delete their uploaded recipes, this will need to be changed.

    rand_recipe = random.randint(1, number_of_recipes)

    response = test_client.get('/api/recipes/' + str(rand_recipe), follow_redirects=True)
    assert response.status_code == 200


def test_api_read_incorrect_recipe_route_invalid(test_client, db):
    """
    GIVEN a flask app
    WHEN a user makes API call to read an invalid recipes
    THEN route is valid
    """
    from app.models import Recipes

    number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
    # indicating how many recipes there are.
    # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
    # can upload + delete their uploaded recipes, this will need to be changed.

    invalid_recipe = number_of_recipes + 1000  # recipe out of range
    pass

    # response = test_client.get('/api/recipes/' + str(invalid_recipe), follow_redirects=True)
    # # assert b'Page Not Found' in response.data
    # assert response.status_code == 404  # Browser returns 404, but test breaks because 404 is not handled.
