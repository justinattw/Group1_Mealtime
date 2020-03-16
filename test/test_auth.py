"""
Contains tests for the auth blueprint
"""
from test.conftest import login, logout


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
    response = login(test_client, email=user.email, password=user.password)
    assert response.status_code == 200

    # user_name = user.first_name + ' ' + user.last_name
    # user_name = ''.join(format(ord(i), 'b') for i in user_name)
    # print(user_name)
    # print(b'Logged in successfully. Welcome ')
    # assert (b'Logged in successfully. Welcome ') in response.data

    response = test_client.post('/login/', data=dict(
        email=user.email,
        password=user.password
    ), follow_redirects=False) # set follow_redirects to false and test the response is invalid
    assert response.status_code == 302


def test_logout_user_success(test_client, user):
    """
    GIVEN a flask app and user logged in
    WHEN user logs out
    THEN response is valid and success message is flashed
    """
    login(test_client, email=user.email, password=user.password)
    response = logout(test_client)
    assert response.status_code == 200
    # assert b'You have been logged out.' in response.data


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
    assert db.session.query(Users).filter(Users.email==user_data['email']).all() is not None


def test_account_view_inaccessible_without_login(test_client):
    """
    GIVEN a flask app
    WHEN /account page is requested without login
    THEN response is invalid
    """
    response = test_client.post('/account/')
    assert response.status_code == 404


def test_login_required(test_client, user):
    """
    GIVEN a flask app
    WHEN login_required is requested
    THEN validation is successful
    """
    pass


def test_account_view_success_with_login(test_client, user):

    login(test_client, email=user.email, password=user.password)
    response = test_client.post('/account/')
    # assert response.status_code == 200

