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

import config
from test.conftest import login, login_test_user, logout, edit_password, edit_preferences, session

import pytest
import random


class TestLoginLogout:


    def test_login_fails_with_unregistered_email(self, test_client):
        """
        GIVEN a flask app
        WHEN a user attempts login with an unregistered email
        THEN an associated error message flashes
        """
        response = login(test_client, email="notregistered@test.com", password='cat123')
        assert b'No account has been registered with this email.' in response.data

    def test_login_fails_with_incorrect_password(self, test_client, user):
        """
        GIVEN a flask app
        WHEN a user attempts login with a registered email but invalid password
        THEN an associated error message flashes
        """
        response = login(test_client, email=user.email, password='invalidpassword')
        assert b'Incorrect password.' in response.data

    def test_login_success_with_valid_user(self, test_client, user):
        """
        GIVEN a flask app
        WHEN a user logs in with valid user details
        THEN 1) response is valid and 2) redirection occurs
        """
        response = login_test_user(test_client)
        assert response.status_code == 200
        assert (b'Logged in successfully. Welcome, Test') in response.data

    def test_logout_user_success(self, test_client, user):
        """
        GIVEN a flask app and user logged in
        WHEN user logs out
        THEN response is valid and success message is flashed
        """
        login_test_user(test_client)
        response = logout(test_client)
        assert response.status_code == 200
        assert b'You have been logged out.' in response.data


class TestSignup:

    def test_register_user_success(self, test_client, user_data):
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


    def test_duplicate_register_error(self, test_client, user):
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
        # Error message associated with ValidationError


class TestLoginRequiredViews:

    def test_account_view_requires_login(self, test_client):
        """
        GIVEN a flask app
        WHEN /account page is requested without login
        THEN response is invalid
        """
        response = test_client.get('/account/')
        assert response.status_code == 302


    def test_account_view_accessible_after_login(self, test_client, user):
        """
        GIVEN a flask app and user logged in
        WHEN /account is requested
        THEN response is valid
        """
        login_test_user(test_client)
        response = test_client.get('/account/')
        assert b'Account details for Test User' in response.data
        assert response.status_code == 200


    def test_edit_preferences_view_requires_login(self, test_client):
        """
        GIVEN a flask app
        WHEN /edit_preferences is requested without login
        THEN response is invalid
        """
        response = test_client.get('/edit_preferences/')
        assert response.status_code == 302  # Method not allowed


    def test_edit_preferences_view_accessible_after_login(self, test_client, user):
        """
        GIVEN a flask app and user is logged in
        WHEN /edit_preferences is requested
        THEN response is invalid
        """
        response = test_client.get('/edit_preferences/')
        assert b'Edit preferences' in response.data
        assert response.status_code == 200


class TestEditPassword:

    def test_check_password(self, test_client, user):
        """
        GIVEN a flask app and a registered user
        WHEN database checks for old password
        THEN old password is correct
        """
        old_password = 'cat123'
        assert user.check_password(old_password) is True  # assert old password is 'cat123'

    def test_change_password_incorrect_old_password_fails(self, test_client, user):
        """
        GIVEN a flask app and user is logged in
        WHEN user tries to change password to a new password, but enters an incorrect old password
        THEN an appropriate error message is flashed, and the password change is not made
        """
        login_test_user(test_client)

        incorrect_old_password = 'elephant999'
        new_password = 'dog123'

        response = edit_password(test_client, incorrect_old_password, new_password, new_password)
        assert b'Incorrect old password' in response.data
        assert user.check_password(new_password) is False

    def test_change_password_success_with_valid_inputs(self, test_client, user):
        """
        GIVEN a flask app and user is logged in
        WHEN user tries to change password to a new password WITH a correct old_password
        THEN an appropriate success message is flashed, new password is set in the database. User can not longer login
            with old password, but success with new password
        """
        old_password = 'cat123'
        new_password = 'dog123'

        response = edit_password(test_client, old_password, new_password, new_password)  # change password to 'dog123'
        assert b'Your password has been changed' in response.data
        assert user.check_password(new_password) is True  # assert password is changed

        response = login_test_user(test_client)  # Logging in with old password
        assert b'Incorrect password.' in response.data

        response = login(test_client, email=user.email, password=new_password)  # login to with new password
        assert response.status_code == 200
        assert b'Logged in successfully. Welcome, ' in response.data


class TestEditPreferences:


    @pytest.mark.parametrize("itr", [(i) for i in range(10)])  # Do test n times
    def test_edit_preferences_response_and_database(self, test_client, user, db, itr):
        """
        GIVEN a flask app and user is logged in
        WHEN /edit_preferences is posted and user has input some random diet preference and allergy
        THEN appropriate response message flashes, and diet_types/ allergies are added in db, while old settings are
            overwritten
        """
        from app.models import UserDietPreferences, UserAllergies

        random_diet = random.randint(1, len(config.DIET_CHOICES))  # set diet type to random diet
        random_allergies = random.sample(range(1, len(config.ALLERGY_CHOICES)), random.randint(2, 6))  # Give user a
        # random set of allergies, ranging from having between 2 to 6 allergies

        response = edit_preferences(test_client, diet_choice=random_diet, allergy_choices=random_allergies)
        assert response.status_code == 200
        assert b'Your food preferences have been updated' in response.data

        all_diet_choices = range(1, len(config.DIET_CHOICES))  # A list of all diet_choice ids
        all_allergy_choices = range(1, len(config.ALLERGY_CHOICES))  # A list of all allergy_choice ids

        for diet in all_diet_choices:
            diet_query = db.session.query(UserDietPreferences) \
                .filter(UserDietPreferences.user_id == user.id) \
                .filter(UserDietPreferences.diet_type_id == diet) \
                .first()
            # 1) if diet equal to what was set previously, then query should not be None (because it should have saved)
            if diet == random_diet:
                assert diet_query is not None
            # 2) if diet_type is NOT set previously, then this query should be None
            else:
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


    def test_edit_preferences_response_with_invalid_duplicate_allergies(self, test_client, user, db):
        """
        GIVEN a flask app and user is logged in
        WHEN /edit_preferences is posted but with an invalid input where there are duplicate allergies
        THEN unique constraint on the composite key in UserAllergies will fail, IntegrityError will occur in SQLAlchemy.
            An error message will therefore flash.
        """
        login_test_user(test_client)
        select_diet = 1
        invalid_allergy_choices = [2, 2]  # Duplicate allergies,

        response = edit_preferences(test_client, diet_choice=select_diet, allergy_choices=invalid_allergy_choices)
        assert b'ERROR! Unable to make preference changes.' in response.data
