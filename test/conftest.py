#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/conftest.py:

Configures settings for Pytest (the selected testing framework for Mealtime). Includes setup and teardowns (fixtures),
as well as helper functions.
"""
__authors__ = "Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import create_app
from app import db as _db
import config

from flask_login import login_user, logout_user
import numpy as np
import random
import pytest


@pytest.yield_fixture(scope='session')
def app(request):
    """Create a test client to send requests to"""
    _app = create_app('config.TestConfig')
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def test_client(app):
    """ Exposes the Werkzeug test client for use in the tests. """
    return app.test_client()


@pytest.yield_fixture(scope='session')
def db(app):
    _db.app = app
    _db.create_all()
    _db.Model.metadata.reflect(_db.engine)

    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def user(test_client, db):
    """ Creates a test user. """
    from app.models import Users, UserDietPreferences, UserAllergies
    user = Users(first_name='Test',
                 last_name='User',
                 email='user@test.com')
    user.set_password('cat123')

    # Set random food preferences (diet types and allergies) for test user
    random_diet_type = random.randint(1, len(config.DIET_CHOICES))
    random_allergies = list(
        set([random.randrange(1, len(config.ALLERGY_CHOICES)) for i in range(random.randint(1, 5))]))
    edit_preferences(test_client, random_diet_type, random_allergies)

    db.session.add(user)
    db.session.commit()
    user_diet_preferences = UserDietPreferences(user_id=user.id,
                                                diet_type_id=random_diet_type)
    db.session.add(user_diet_preferences)

    for allergy in random_allergies:
        user_allergy = UserAllergies(user_id=user.id,
                                     allergy_id=allergy)
        db.session.add(user_allergy)

    db.session.commit()

    return user


@pytest.fixture(scope='function')
def vegan_user(test_client, db):
    """ Creates a test user who is vegan."""
    from app.models import Users, UserDietPreferences, UserAllergies
    user = Users(first_name='Vegan',
                 last_name='User',
                 email='veganuser@test.com')
    user.set_password('GoVegan')

    # Set random food preferences (diet types and allergies) for test user
    random_diet_type = 4 # set user to be vegan
    random_allergies = random.sample(range(1, len(config.ALLERGY_CHOICES) + 1), random.randint(2, 6))
    # random_allergies = list(
    #     set([random.randrange(1, len(config.ALLERGY_CHOICES)) for i in range(random.randint(1, 5))]))
    print(random_allergies)
    edit_preferences(test_client, random_diet_type, random_allergies)

    db.session.add(user)
    db.session.commit()
    user_diet_preferences = UserDietPreferences(user_id=user.id,
                                                diet_type_id=random_diet_type)
    db.session.add(user_diet_preferences)

    for allergy in random_allergies:
        user_allergy = UserAllergies(user_id=user.id,
                                     allergy_id=allergy)
        db.session.add(user_allergy)

    db.session.commit()

    return user


@pytest.fixture(scope='function', autouse=True)
def session(db):
    """ Rolls back database changes at the end of each test """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.fixture(scope='function')
def logged_in_user(app, request, user):
    """ Creates a logged in user and logs them out again when the test is complete using Flask-Login """
    with app.test_request_context():
        login_user(user)

    request.addfinalizer(logout_user)


@pytest.fixture(scope='function')
def user_data():
    """ Provides the details for a user registration. """
    user_data = {
        "first_name": "Signup",
        "last_name": "Test",
        "email": "signup@test.com",
        "password": "dog123",
        "confirm": "dog123"
    }
    return user_data


# Test browser configurations
import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    return driver


# Helper functions (not fixtures) from https://flask.palletsprojects.com/en/1.1.x/testing/
def login(client, email, password):
    return client.post('/login/', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def login_test_user(client):
    return client.post('/login/', data=dict(
        email="user@test.com",
        password="cat123"
    ), follow_redirects=True)


def login_vegan_test_user(client):
    return client.post('/login/', data=dict(
        email="veganuser@test.com",
        password="GoVegan"
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout/', follow_redirects=True)


def edit_password(client, old_password, new_password, confirm_password):
    return client.post('/edit_password/', data=dict(
        old_password=old_password,
        new_password=new_password,
        confirm_password=confirm_password
    ), follow_redirects=True)


def edit_preferences(client, diet_choice, allergy_choices):
    return client.post('/edit_preferences/', data=dict(
        diet_type=diet_choice,
        allergies=allergy_choices
    ), follow_redirects=True)


def search_function(client, search_term):
    return client.post('/search', data=dict(
        search_term=search_term,
    ), follow_redirects=True)


def add_to_favourites(client, recipe_id):
    url_str = '/add_to_favourites/' + str(recipe_id)
    return client.post(url_str, data=dict(
        recipe_id=recipe_id
    ), follow_redirects=True)


def view_recipe(client, recipe):
    url_str = '/recipe/' + str(recipe)
    return client.get(url_str, follow_redirects=True)


def view_favourites(client):
    return client.get('/favourites', follow_redirects=True)


def view_about(client):
    return client.get('/about', follow_redirects=True)


def view_mealplanner(client):
    return client.get('/mealplanner', follow_redirects=True)


def view_create_mealplan(client):
    return client.get('/create_new_mealplan/', follow_redirects=True)
