"""
Contains tests for the auth blueprint
"""
from test.conftest import login


def test_login_fails_with_invalid_input(test_client, app):
    # Test invalid email
    response = login(test_client, email="not_registered@test.com", password='cat123')
    assert b'No account has been registered with this email.' in response.data

    # Test invalid password
    response = login(test_client, email="not_registered@test.com", password='cat123')
    assert b'Incorrect password.' in response.data


def test_login_success_with_valid_user(test_client, user):
    response = test_client.post('/login/', data=dict(
        email=user.email,
        password=user.password
    ), follow_redirects=True)
    assert response.status_code == 200


def test_register_user_success(user_data, test_client):
    response = test_client.post('/signup/', data=dict(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        password=user_data['password'],
        confirm=user_data['confirm']
    ), follow_redirects=True)
    assert response.status_code == 200
