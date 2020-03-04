"""
Contains tests for the auth blueprint
"""
# from test.pytest_tests.conftest import login
from conftest import login


def test_login_fails_with_invalid_email(test_client, app):
    response = login(test_client, email="notareal@email.com", password='Fake')
    assert b'Invalid username or password' in response.data


def test_login_success_with_valid_user(test_client, user):
    response = test_client.post('/login/', data=dict(
        email=user.email,
        password=user.password
    ), follow_redirects=True)
    assert response.status_code == 200

def test_login(test_client, user):
    response = login(test_client, user)
    assert response.status_code == 200


def test_register_student_success(user_data, test_client):
    response = test_client.post('/signup/', data=dict(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        password=user_data['password'],
        confirm=user_data['confirm']
    ), follow_redirects=True)
    assert response.status_code == 200