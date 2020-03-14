"""
Contains the functional tests for the main blueprint.
"""
from flask_login import current_user

from test.conftest import login


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
    assert b'Welcome' in response.data


def test_profile_displayed_when_user_logged_in(test_client, user):
    login(test_client, password=user.password, email=user.email)
    response = test_client.get('/view_profile/')
    assert response.status_code == 200
    print(response.data)
    assert b'Account type: Student' in response.data


def test_view_profile_not_allowed_when_user_not_logged_in(test_client):
    """
    Exercise: Write a test for the following case
    GIVEN a Flask application
    WHEN the ‘/view_profile' page is requested (GET) when the user is not logged in
    THEN the user is redirected to the login page and the message ‘You must be logged in to view that page.’ is displayed
    """
    # response(/)
    pass
