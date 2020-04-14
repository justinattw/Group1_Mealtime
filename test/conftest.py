#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/conftest.py:

Configures settings for Pytest (the selected testing framework for Mealtime). Includes setup and teardowns (fixtures),
as well as helper functions.
"""

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import create_app
from app import db as _db
import config

from flask_login import login_user, logout_user
import pytest
import random
from urllib.request import urlopen


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
    # User has a random number of between 1-5 allergies, and random allergies
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


# Test browser configuration. The following code is adapted from a tutorial
# Title: Set Your Test Automation Goals with Web UI Testing
# Author: AutomationPanda
# Date: 2019
# Availability: https://blog.testproject.io/2019/07/16/test-automation-goals-with-web-ui-testing/
# Accessed: 6 April 2020
from selenium import webdriver

from flask import url_for


@pytest.fixture
def browser():
    """ Sets up driver for Selenium browser testing """
    # (NOT RECOMMENDED) Use following driver if chromedriver is in PATH.
    # # path = "join(os.getcwd() + 'chromedriver/chromedriver')"  # Mac
    # path = "join(os.getcwd() + 'chromedriver/chromedriver.exe')"  # Windows
    # driver = webdriver.Chrome(executable_path=path)

    # (RECOMMENDED) Use following driver if chromedriver is in PATH.
    # To move chromedriver to PATH, just copy the chromedriver from test/chromedriver to venv/bin
    driver = webdriver.Chrome()  # CircleCI. Activate this when committing to GitHub.

    driver.implicitly_wait(10)
    yield driver
    driver.close()


@pytest.mark.usefixtures('live_server')
class TestLiveServer:

    def test_server_is_up_and_running(self):
        res = urlopen(url_for('index', _external=True))
        assert b'OK' in res.read()
        assert res.code == 200


@pytest.fixture(scope='function')
def browser_user_data():
    """ Provides the details for a browser user registration. """
    user_data = {
        "first_name": "Bowser",
        "last_name": "User",
        "email": "bowser@user.com",
        "password": "bowsersCastle",
        "confirm": "bowsersCastle"
    }
    return user_data


# Client helper functions (not fixtures) from https://flask.palletsprojects.com/en/1.1.x/testing/
def get_recipe_ids(client, response):
    """
    Gets recipe ids from any recipes view, such as /recipes or /favourites

    :return: a list of all recipe_ids on page
    """
    response_recipe_ids = []
    page_string = response.data.decode()
    page_list = page_string.split('a href="/recipe/')
    page_index = 0
    for item in page_list:
        if page_index == 0:
            pass
        else:
            item_recipe_id = item.split('">')[0]
            item_recipe_id = item_recipe_id.strip()
            response_recipe_ids.append(int(item_recipe_id))
        page_index += 1

    return response_recipe_ids


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


def advanced_search_function(client, search_term="", allergy_list=[], diet_type=1, cal_range="0,1000", time=1000):
    return client.post('/advanced_search', data=dict(
        search_term=search_term,
        allergy_list=allergy_list,
        diet_type=diet_type,
        hidden=cal_range,
        hidden2=time
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


def remove_from_favourites(client, recipe_id):
    return client.post('/remove_from_favourites/' + str(recipe_id), data=dict(
        recipe_id=recipe_id
    ), follow_redirects=True)


def view_all_recipes(client):
    return client.get('/view_all_recipes', follow_redirects=True)


def view_about(client):
    return client.get('/about', follow_redirects=True)


def view_advanced_search(client):
    return client.get('/advanced_search', follow_redirects=True)


def create_mealplan(client):
    return client.post('/mealplanner', follow_redirects=True)


def add_to_mealplan(client, recipeid):
    return client.post('/add_to_mealplan/' + str(recipeid), data=dict(
        recipeid=recipeid
    ), follow_redirects=True)


def view_mealplan(client, mealplan_id):
    meal_string = str(mealplan_id)
    return client.get('/view_mealplan/' + meal_string, follow_redirects=True)


def del_from_mealplan(client, mealplan_id, recipe_id):
    delete_string = str(mealplan_id) + '/' + str(recipe_id)
    return client.post('/del_from_mealplan/' + delete_string, data=dict(
        mealplan_id=mealplan_id,
        recipe_id=recipe_id
    ), follow_redirects=True)


def view_grocery_list(client, mealplan_id):
    meal_string = str(mealplan_id)
    return client.post('/grocery_list/' + meal_string, data=dict(
        mealplan_id=mealplan_id
    ), follow_redirects=True)


def delete_mealplan(client, mealplan_id):
    delete_string = str(mealplan_id)
    return client.post('/del_mealplan/' + delete_string, data=dict(
        mealplan_id=mealplan_id
    ), follow_redirects=True)


def send_grocery_list(client, mealplan_id):
    return client.get('/send_grocery_list/' + str(mealplan_id), data=dict(
        mealplan_id=mealplan_id
    ), follow_redirects=True)


# Browser helper functions
def browser_signup(browser, browser_user_data):
    signup_url = url_for('auth.signup', _external=True)

    browser.get(signup_url)
    form_first_name = browser.find_element_by_id('signup_first_name')
    form_last_name = browser.find_element_by_id('signup_last_name')
    form_email = browser.find_element_by_id('signup_email')
    form_password = browser.find_element_by_id('signup_password')
    form_confirm = browser.find_element_by_id('signup_confirm')
    form_submit = browser.find_element_by_id("submit_button")

    form_first_name.send_keys(browser_user_data["first_name"])
    form_last_name.send_keys(browser_user_data["last_name"])
    form_email.send_keys(browser_user_data["email"])
    form_password.send_keys(browser_user_data["password"])
    form_confirm.send_keys(browser_user_data["confirm"])
    form_submit.click()


def browser_login(browser, user_data):
    login_url = url_for('auth.login', _external=True)
    browser.get(login_url)

    form_email = browser.find_element_by_id('login-email')
    form_password = browser.find_element_by_id('login-password')
    form_submit = browser.find_element_by_css_selector('.btn.btn-primary')

    form_email.send_keys(user_data["email"])
    form_password.send_keys(user_data["password"])
    form_submit.click()
