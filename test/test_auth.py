"""
Contains tests for the auth blueprint
"""
from test.conftest import login


def test_login_fails_with_invalid_username(test_client, app):
    response = login(test_client, email="faketest@email", password='cat123')
    assert b'Invalid username or password' in response.data


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

def test_register_user_success(user_data, test_client):
    response = test_client.post('/signup/', data=dict(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        password=user_data['password'],
        confirm=user_data['confirm']
    ), follow_redirects=True)
    assert response.status_code == 200
