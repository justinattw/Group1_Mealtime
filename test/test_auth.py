"""
Contains tests for the auth blueprint
"""
from test.conftest import login, logout, edit_password
import pytest



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
    print(response.data)
    assert response.status_code == 200
    assert b'Logged in successfully' in response.data
    assert (b'Logged in successfully. Welcome, Test') in response.data
    # user_name = ''.join(format(ord(i), 'b') for i in user.first_name)
    # print(user_name)
    # print(b'Logged in successfully. Welcome ' + user_name)
    # assert (b'Logged in successfully. Welcome, ' + user_name) in response.data


#    response = test_client.post('/login/', data=dict(
#        email=user.email,
#        password=user.password
#    ), follow_redirects=False)  # set follow_redirects to false and test the response is invalid
#    assert response.status_code == 302


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


def test_register_user_success(test_client, user_data, db):
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

    from app.models import Users
    # assert db.session.query(Users).filter(Users.email == user_data['email']).all() is not None


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
    print(response.data)
 #   print(user.email)
 #   print(user.password)
 #   print(test_client.post('/account/'))
    assert b'Account details for Test User' in response.data
    assert response.status_code == 200


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


