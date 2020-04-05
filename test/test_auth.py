#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_auth.py:

Pytests tests for authentication views and methods (relating to files in app/auth/)
"""

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import config
from test.conftest import login, login_test_user, logout, edit_password, edit_preferences, session

import random


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
    response = test_client.post('/signup/', data=dict(
        first_name="Test",
        last_name="Name",
        email=user.email,  # attempt signup with email of registered user
        password="cat123",
        confirm="cat123"
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'An account is already registered with this email.' in response.data


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


def test_edit_password(test_client, user):
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


def test_edit_preferences_response_and_database(test_client, user, db):
    """
    GIVEN a flask app and user is logged in
    WHEN /edit_preferences is requested and user has input some random diet preference and allergy
    THEN response is valid
    """
    from app.models import UserDietPreferences, UserAllergies

    random_diet = random.randint(2, len(config.DIET_CHOICES)+1)  # set diet type to random diet NOT classic
    random_allergies = random.sample(range(1, len(config.ALLERGY_CHOICES)+1), random.randint(2, 6))  # Give user a random
    # set of allergies, ranging having from 2 to 6 allergies

    response = edit_preferences(test_client, diet_choice=random_diet, allergy_choices=random_allergies)
    assert b'Your food preferences have been updated' in response.data
    assert response.status_code == 200

    """
    GIVEN a flask app and user is logged in
    WHEN /edit_preferences is requested and user has input some random diet preference and allergy
    THEN 1) database updates with new selected diet type, and 2) incorrect diet/ allergies are not in the database.
    """
    # 1
    diet_query = db.session.query(UserDietPreferences) \
        .filter(UserDietPreferences.user_id == user.id) \
        .filter(UserDietPreferences.diet_type_id == random_diet) \
        .first()
    assert diet_query is not None

    for allergy in random_allergies:
        allergy_query = db.session.query(UserAllergies) \
            .filter(UserAllergies.user_id == user.id) \
            .filter(UserAllergies.allergy_id == allergy) \
            .first()
        assert allergy_query is not None

    #2
    # List of diet types NOT equal to random diet type set earlier
    wrong_diets = [i for i in range(1, len(config.DIET_CHOICES)+1) if i != random_diet]
    # List of allergies NOT equal to random allergies set earlier
    wrong_allergies = [i for i in range(1, len(config.ALLERGY_CHOICES)+1) if i not in random_allergies]

    # Assert that there is no 'residual' diet/ allergy types stored in the database
    for diet in wrong_diets:
        diet_query = db.session.query(UserDietPreferences) \
            .filter(UserDietPreferences.user_id == user.id) \
            .filter(UserDietPreferences.diet_type_id == diet) \
            .first()
        assert diet_query is None

    for allergy in wrong_allergies:
        allergy_query = db.session.query(UserAllergies) \
            .filter(UserAllergies.user_id == user.id) \
            .filter(UserAllergies.allergy_id == allergy) \
            .first()
        assert allergy_query is None