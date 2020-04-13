#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_auth.py:

Pytests tests for authentication views and methods (relating to files in app/auth/).

app/auth COVERAGE: 90%

We achieve 90% coverage of the app/auth directory, but the uncovered sections seem to be code that we cannot trigger
deliberately through the routes (such as IntegrityError for signing up), because there are form validations and route
validations that prevent them from occurring.
"""

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import pytest

import config
from test.conftest import login, login_test_user, logout, edit_password, edit_preferences, session

import random
from wtforms.validators import ValidationError


def test_login_fails_with_invalid_input(test_client, user):
    """
    GIVEN a flask app
    WHEN a user attempts login with an unregistered email
    THEN an associated error message flashes
    """
    response = login(test_client, email="notregistered@test.com", password='cat123')
    assert b'No account has been registered with this email.' in response.data

    """
    GIVEN a flask app
    WHEN a user attempts login with a registered email but invalid password
    THEN an associated error message flashes
    """
    response = login(test_client, email=user.email, password='invalidpassword')
    assert b'Incorrect password.' in response.data


def test_login_success_with_valid_user(test_client, user):
    """
    GIVEN a flask app
    WHEN a user logs in with valid user details
    THEN 1) response is valid and 2) redirection occurs
    """
    response = login_test_user(test_client)
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data
    assert (b'Logged in successfully. Welcome, Test') in response.data


def test_logout_user_success(test_client, user):
    """
    GIVEN a flask app and user logged in
    WHEN user logs out
    THEN response is valid and success message is flashed
    """
    login_test_user(test_client)
    response = logout(test_client)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data


def test_register_user_success(test_client, user_data):
    """
    GIVEN a flask app
    WHEN a user registers with valid user details
    THEN response is valid and user is added to database
    """
    response = test_client.post('/signup/', data=dict(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        password=user_data['password'],
        confirm=user_data['confirm']
    ), follow_redirects=True)
    assert response.status_code == 200


def test_duplicate_register_error(test_client, user):
    """
    GIVEN a flask app
    WHEN user registers new account with pre-registered email
    THEN appropriate validation error is raised
    """
    # with pytest.raises(ValidationError):  # Not sure how to trigger validation error in forms

    response = test_client.post('/signup/', data=dict(
        first_name="Test",
        last_name="Name",
        email=user.email,  # attempt signup with email of registered user
        password="cat123",
        confirm="cat123"
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'An account is already registered with this email.' in response.data  # Error message associated with
    # ValidationError


def test_account_view_requires_login(test_client):
    """
    GIVEN a flask app
    WHEN /account page is requested without login
    THEN response is invalid
    """
    response = test_client.post('/account/')
    assert response.status_code == 405  # Method not allowed


def test_account_view_accessible_after_login(test_client, user):
    """
    GIVEN a flask app and user logged in
    WHEN /account is requested
    THEN response is valid
    """
    login_test_user(test_client)
    response = test_client.get('/account/')
    assert b'Account details for Test User' in response.data
    assert response.status_code == 200


def test_edit_password_with_valid_and_invalid_inputs(test_client, user):
    """
    GIVEN a flask app and a registered user
    WHEN database checks for old password
    THEN old password is correct
    """
    old_password = 'cat123'
    assert user.check_password(old_password) is True  # assert old password is 'cat123'

    """
    GIVEN a flask app and user is logged in
    WHEN user tries to change password to a new password, but enters an incorrect old password
    THEN an appropriate error message is flashed, and the password change is not made
    """
    incorrect_old_password = 'elephant999'
    new_password = 'dog123'
    response = edit_password(test_client, incorrect_old_password, new_password, new_password)
    assert b'Incorrect old password' in response.data
    assert user.check_password(new_password) is False

    """
    GIVEN a flask app and user is logged in
    WHEN user tries to change password to a new password WITH a correct old_password
    THEN an appropriate success message is flashed, and new password is set in the database
    """
    response = edit_password(test_client, old_password, new_password, new_password)  # change password to 'dog123'
    assert b'Your password has been changed' in response.data
    assert user.check_password(new_password) is True  # assert password is changed

    """
    GIVEN a flask app
    WHEN user tries to log in with the old password (now it is incorrect)
    THEN an appropriate error message is flashed and login fails, because the password has been changed
    """
    response = login_test_user(test_client)
    assert b'Incorrect password.' in response.data

    """
    GIVEN a flask app
    WHEN user tries to log in with the new password (which is correct)
    THEN an appropriate success message is flashed and user is logged in
    """
    response = login(test_client, email=user.email, password=new_password)  # login to test user with test password
    assert response.status_code == 200
    assert b'Logged in successfully. Welcome, ' in response.data


def test_edit_preferences_view_requires_login(test_client):
    """
    GIVEN a flask app
    WHEN /edit_preferences is requested without login
    THEN response is invalid
    """
    response = test_client.get('/edit_preferences/')
    assert response.status_code == 302  # Method not allowed


def test_edit_preferences_view_accessible_after_login(test_client, user):
    """
    GIVEN a flask app and user is logged in
    WHEN /edit_preferences is requested
    THEN response is invalid
    """
    response = test_client.get('/edit_preferences/')
    assert b'Edit preferences' in response.data
    assert response.status_code == 200


def test_edit_preferences_response_and_database(test_client, user, db):
    """
    GIVEN a flask app and user is logged in
    WHEN /edit_preferences is posted and user has input some random diet preference and allergy
    THEN response is valid and appropriate response message flashes
    """
    from app.models import UserDietPreferences, UserAllergies

    random_diet = random.randint(2, len(config.DIET_CHOICES) + 1)  # set diet type to random diet NOT classic
    random_allergies = random.sample(range(1, len(config.ALLERGY_CHOICES) + 1), random.randint(2, 6))  # Give user a
    # random set of allergies, ranging from having between 2 to 6 allergies (an arbitrary number)

    response = edit_preferences(test_client, diet_choice=random_diet, allergy_choices=random_allergies)
    assert response.status_code == 200
    assert b'Your food preferences have been updated' in response.data

    """
    GIVEN a flask app and user is logged in
    WHEN /edit_preferences is posted and user has input some random diet preference and allergy
    THEN inputted diet_type/ allergies are added to db, and non-inputted diet_types/ allergies are not in db 
    """
    all_diet_choices = range(1, len(config.DIET_CHOICES) + 1)  # A list of all diet_choice ids
    all_allergy_choices = range(1, len(config.ALLERGY_CHOICES) + 1)  # A list of all allergy_choice ids

    for diet in all_diet_choices:
        diet_query = db.session.query(UserDietPreferences) \
            .filter(UserDietPreferences.user_id == user.id) \
            .filter(UserDietPreferences.diet_type_id == diet) \
            .first()
        if diet == random_diet:  # 1) if diet type is the one set previously, then query should not be None
            assert diet_query is not None
        else:  # 2) if diet_type is NOT set previously, then query should be None
            assert diet_query is None

    for allergy in all_allergy_choices:
        allergy_query = db.session.query(UserAllergies) \
            .filter(UserAllergies.user_id == user.id) \
            .filter(UserAllergies.allergy_id == allergy) \
            .first()
        if allergy in random_allergies:  # 1) if allergy is one selected previously, then query should not be None
            assert allergy_query is not None
        else:  # 2) if allergy is NOT set previously, then query should be None
            assert allergy_query is None


def test_edit_preferences_response_with_invalid_duplicate_allergies(test_client, user, db):
    """
    GIVEN a flask app and user is logged in
    WHEN /edit_preferences is posted but with an invalid input where there are duplicate allergies
    THEN unique constraint on the composite key in UserAllergies will fail, IntegrityError will occur in SQLAlchemy.
        An error message should flash, though the allergy may still be added on the first occurrence, so a success
        message will also flash.
    """
    login_test_user(test_client)
    select_diet = 1
    invalid_allergy_choices = [2, 2]  # Duplicate allergies,

    response = edit_preferences(test_client, diet_choice=select_diet, allergy_choices=invalid_allergy_choices)
    assert b'ERROR! Unable to make preference changes.' in response.data
    assert b'Your food preferences have been updated' in response.data
