#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_auth.py:

Pytests tests for authentication views and methods (relating to files in app/auth/).

app/auth COVERAGE: 100% files, 90% lines covered

We achieve 90% coverage of the app/auth directory, but the uncovered sections seem to be code that we cannot trigger
deliberately through the routes (such as IntegrityError for signing up), because there are form validations and route
validations that prevent them from occurring. Most untested sections are final failsafes (excepts) in case the
connection to SQLAlchemy database fails
"""

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import config
from test.conftest import login, login_test_user, logout, edit_password, edit_preferences, session

from flask import url_for
import pytest
import random

MIN_PW_LEN = config.MIN_PW_LEN
MAX_PW_LEN = config.MAX_PW_LEN

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

    def test_logout_user_success(self, test_client, user, logged_in_user):
        """
        GIVEN a flask app and user logged in
        WHEN user logs out
        THEN response is valid and success message is flashed
        """
        response = logout(test_client)
        assert response.status_code == 200
        assert b'You have been logged out.' in response.data


class TestSignup:

    def test_signup_user_success(self, test_client, user_data):
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

    def test_duplicate_email_register_error(self, test_client, user):
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

    def test_register_email_case_insensitive_success(self, test_client, db):
        """
        GIVEN a flask app
        WHEN user registers an account and the email has capital letters
        THEN the email is turned to lower case, and you can log in with lower cased email
        """
        case_insensitive_email = "cAsEiNsEnSiTiVe@EmAiL.CoM"
        lower_email = case_insensitive_email.lower()
        password = "cat123"

        test_client.post('/signup/', data=dict(
            first_name="Test",
            last_name="Name",
            email=case_insensitive_email,  # attempt signup with email of registered user
            password=password,
            confirm=password
        ), follow_redirects=True)

        logout(test_client)
        response = login(test_client, email=lower_email, password=password)  # login with lower_email
        assert response.status_code == 200
        assert (b'Logged in successfully. Welcome, Test') in response.data

    def test_signup_email_format_validator(self, test_client):
        """
        GIVEN a flask app
        WHEN user registers account with an email in the wrong format
        THEN appropriate validation error is raised
        """
        invalid_format_email = "thisIsNotAnEmail"

        response = test_client.post('/signup/', data=dict(
            first_name="Test",
            last_name="Name",
            email=invalid_format_email,  # attempt signup with email of registered user
            password='cat123',
            confirm='cat123'
        ), follow_redirects=True)
        assert b'Valid email address required' in response.data

    def test_signup_both_passwords_must_match(self, test_client, user_data):
        """
        GIVEN a flask app
        WHEN user registers account but password and confirm-password don't match
        THEN appropriate validation error is raised
        """
        password1 = 'cat123'
        password2 = 'dog123'

        response = test_client.post('/signup/', data=dict(
            first_name="Test",
            last_name="Name",
            email=user_data['email'],  # attempt signup with email of registered user
            password=password1,
            confirm=password2
        ), follow_redirects=True)
        assert b'The passwords do not match' in response.data

    def test_signup_password_length_validator_too_short_password(self, test_client, user_data):
        """
        GIVEN a flask app
        WHEN user registers new account too short password
        THEN appropriate validation error is raised
        """
        # password must be between 6 and 20 characters
        too_short_password = "12345" # 5 characters

        response = test_client.post('/signup/', data=dict(
            first_name="Test",
            last_name="Name",
            email=user_data['email'],  # attempt signup with email of registered user
            password=too_short_password,
            confirm=too_short_password
        ), follow_redirects=True)
        error_message = f'Password must be between {MIN_PW_LEN} and {MAX_PW_LEN} characters long.'
        assert error_message.encode() in response.data

    def test_signup_password_length_validator_too_long_password(self, test_client, user_data):
        """
        GIVEN a flask app
        WHEN user registers new account too long password
        THEN appropriate validation error is raised
        """
        # password must be between 6 and 20 characters
        too_long_password = "123456789012345678901" # 21 characters

        response = test_client.post('/signup/', data=dict(
            first_name="Test",
            last_name="Name",
            email=user_data['email'],  # attempt signup with email of registered user
            password=too_long_password,
            confirm=too_long_password
        ), follow_redirects=True)
        error_message = f'Password must be between {MIN_PW_LEN} and {MAX_PW_LEN} characters long.'
        assert error_message.encode() in response.data


class TestLoginRequiredViews:

    def test_account_view_requires_login(self, test_client):
        """
        GIVEN a flask app
        WHEN /account page is requested without login
        THEN response is invalid
        """
        response = test_client.get('/account/')
        assert response.status_code == 302
        assert url_for('auth.login') in response.location

    def test_account_view_accessible_after_login(self, test_client, logged_in_user):
        """
        GIVEN a flask app and user logged in
        WHEN /account is requested
        THEN response is valid
        """
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

    def test_edit_preferences_view_accessible_after_login(self, test_client, logged_in_user):
        """
        GIVEN a flask app and user is logged in
        WHEN /edit_preferences is requested
        THEN response is valid and correct data is displayed
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

    def test_edit_password_success_with_valid_inputs(self, test_client, user, logged_in_user):
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

    def test_edit_password_incorrect_old_password_validator(self, test_client, user, logged_in_user):
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

    def test_edit_password_both_passwords_must_match(self, test_client, user, logged_in_user):
        """
        GIVEN a flask app and user is logged in
        WHEN user edits password but password and confirm-password don't match
        THEN appropriate validation error is raised
        """
        old_password = 'cat123'
        new_password1 = 'dog321'
        new_password2 = 'dog123'

        response = edit_password(test_client, old_password, new_password1, new_password2)
        assert b'The passwords do not match' in response.data

    def test_edit_password_old_cannot_equal_new_validator(self, test_client, user, logged_in_user):
        """
        GIVEN a flask app and user is logged in
        WHEN user tries to 'change' password to the same old password
        THEN an appropriate error message is flashed, as you cannot change to current password
        """
        old_password = 'cat123'  # Use old password for all inputs
        response = edit_password(test_client, old_password, old_password, old_password)

        # Apostrophe turns to &#39;t in response.data
        # Response.data:    "You can&#39;t set your new password to the current password."
        # Intended message: "You can't set your new password to the current password"
        # Break up the assert message
        assert (b"You can" in response.data) and \
               (b"t set your new password to the current password." in response.data)

    def test_edit_password_password_length_validator_too_short_password(self, test_client, logged_in_user):
        """
        GIVEN a flask app
        WHEN user registers new account too short password
        THEN appropriate validation error is raised
        """
        # password must be between 6 and 20 characters
        too_short_password = "12345" # 5 characters

        response = edit_password(test_client, 'cat123', too_short_password, too_short_password)
        error_message = f'Password must be between {MIN_PW_LEN} and {MAX_PW_LEN} characters long.'
        assert error_message.encode() in response.data

    def test_edit_password_password_length_validator_too_long_password(self, test_client, logged_in_user):
        """
        GIVEN a flask app
        WHEN user registers new account too long password
        THEN appropriate validation error is raised
        """
        # password must be between 6 and 20 characters
        too_long_password = "123456789012345678901" # 21 characters

        response = edit_password(test_client, 'cat123', too_long_password, too_long_password)
        error_message = f'Password must be between {MIN_PW_LEN} and {MAX_PW_LEN} characters long.'
        assert error_message.encode() in response.data


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

    def test_edit_preferences_response_with_invalid_duplicate_allergies(self, test_client, user, logged_in_user):
        """
        GIVEN a flask app and user is logged in
        WHEN /edit_preferences is posted but with an invalid input where there are duplicate allergies
        THEN unique constraint on the composite key in UserAllergies will fail, IntegrityError will occur in SQLAlchemy.
            An error message will therefore flash.
        """
        select_diet = 1
        invalid_allergy_choices = [2, 2]  # Duplicate allergies,

        response = edit_preferences(test_client, diet_choice=select_diet, allergy_choices=invalid_allergy_choices)
        assert b'ERROR! Unable to make preference changes.' in response.data
