#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_auth.py:

Pytests tests for authentication methods (relating to files in app/auth/)
"""


__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

from test.conftest import login, logout, edit_password, edit_preferences, session
import config
import numpy as np



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
    response = login(test_client, email=user.email, password='cat123')
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data
    assert (b'Logged in successfully. Welcome, Test') in response.data


def test_logout_user_success(test_client, user):
    """
    GIVEN a flask app and user logged in
    WHEN user logs out
    THEN response is valid and success message is flashed
    """
    login(test_client, email=user.email, password='cat123')
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

    response = login(test_client, email=user.email, password='cat123')
    response = test_client.get('/account/')
    assert b'Account details for Test User' in response.data
    assert response.status_code == 200

def test_edit_preferences(test_client, user, db):
    from app.models import UserDietPreferences, UserAllergies
    login(test_client, email=user.email, password='cat123')
    full_diet_choices = config.DIET_CHOICES
    full_allergy = config.ALLERGY_CHOICES
    random_diet = np.random.randint(1, 4)
    random_allergy = np.random.randint(1, len(full_allergy))
    response = edit_preferences(test_client, DIET_CHOICES=random_diet, ALLERGY_CHOICES=random_allergy)

    assert b'Your food preferences have been updated' in response.data
    diet_query = db.session.query(UserDietPreferences).filter(UserDietPreferences.user_id == user.id).filter(UserDietPreferences.diet_type_id == random_diet).first()
    allergy_query = db.session.query(UserAllergies).filter(UserAllergies.user_id == user.id).filter(UserAllergies.allergy_id == random_allergy).first()
    assert diet_query is not None
    assert allergy_query is not None


def test_edit_password_success(test_client, user):
    old_password = 'cat123'
    assert user.check_password(old_password) is True  # assert old password is 'cat123'

    login(test_client, email=user.email, password=old_password)  # login to test user

    new_password = "dog123"
    response = edit_password(test_client, old_password, new_password, new_password)  # change password to 'dog123'

    assert b'Your password has been changed' in response.data
    assert user.check_password(new_password) is True  # assert password is changed
    logout(test_client)

    response = login(test_client, email=user.email, password=new_password)  # login to test user
    assert response.status_code == 200
