import unittest

from flask import url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import Users


class BaseTestCase(TestCase):
    """Base test case."""

    def create_app(self):
        app = create_app('config.TestConfig')
        return app

    def setUp(self):

        # create test data
        
        self.user = Users(first_name="Justin", last_name="Test", email="justinattw@test.com")
        self.user.set_password('test123')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        # Called at the end of every test
        db.session.remove()
        # db.drop_all()

    def login(self, email, password):
        return self.client.post(
            '/login/',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get(
            '/logout/',
            follow_redirects=True
        )

    def signup(self, name, title, role, uni_id, email, password, confirm):
        return self.client.post(
            '/signup/',
            data=dict(name=name, title=title, uni_id=uni_id, email=email, password=password, confirm=confirm,
                      role=role),
            follow_redirects=True
        )

    # Provides the details for a user.
    user_data = dict(first_name='Justin', last_name='Test', email='justinattw@test.com', password='test', confirm='test')


class TestMain(BaseTestCase):

    def test_index_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_content(self):
        """
            GIVEN a Flask application
            WHEN the '/' home page is requested
            THEN check the response contains "Welcome!"
            """
        response = self.client.get('/')
        self.assertIn(b'Welcome', response.data)

    def test_profile_not_allowed_when_user_not_logged_in(self):
        """
        Test that view profile is inaccessible without login
        and redirects to login page and then the profile
        """
        target_url = url_for('main.view_profile')
        redirect_url = url_for('auth.login', next=target_url)
        redirect_url = url_for('auth.login')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_profile_displays_when_user_logged_in(self):
        """
            GIVEN a Flask application
            WHEN the '/' profile page is requested with a logged in user
            THEN check the response contains <name>
            Note: This is an integration test rather than a unit test as it tests a sequence of interacting behaviours
        """
        self.login(email='cs1234567@ucl.ac.uk', password='cs1234567')
        target_url = url_for('main.view_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email address: cs1234567@ucl.ac.uk', response.data)

    def test_view_profile_redirects_to_login_when_user_not_logged_in(self):
        """
        Exercise: Write a test for the following case
        GIVEN a Flask application
        WHEN the ‘/view_profile' page is requested (GET) when the user is not logged in
        THEN the user is redirected to the login page
        Hint: try assertRedirects
        """
        target_url = url_for('main.view_profile')
        redirect_url = url_for('auth.login')
        response = self.client.get('target_url')
        self.assertRedirects(response, redirect_url)



class TestAuth(BaseTestCase):

    def test_registration_form_displays(self):
        target_url = url_for('auth.signup')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Signup', response.data)

    def test_register_student_success(self):
        count = Student.query.count()
        response = self.client.post(url_for('auth.signup'), data=dict(
            email=self.student_data.get('email'),
            password=self.student_data.get('password'),
            name=self.student_data.get('name'),
            title=self.student_data.get('title'),
            role=self.student_data.get('role'),
            uni_id=self.student_data.get('uni_id'),
            confirm=self.student_data.get('confirm')
        ), follow_redirects=True)
        count2 = Student.query.count()
        self.assertEqual(count2 - count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login_fails_with_invalid_details(self):
        response = self.login(email='john@john.com', password='Fred')
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_succeeds_with_valid_details(self):
        response = self.login(email='cs1234567@ucl.ac.uk', password='cs1234567')
        self.assertIn(b'Welcome Ahmet Roth', response.data)


class TestModel(BaseTestCase):
    def test_course_model(self):
        """
        Test number of records in Course table
        """
        course = Course(name="A new course", course_code="CS888888", teacher_id=1)
        count = Course.query.count()
        db.session.add(course)
        db.session.commit()
        count2 = Course.query.count()
        self.assertEqual(count2 - count, 1)


class UserModelTestCase(unittest.TestCase):
    # def test_password_setter(self):
    #     u = Users(password = 'cat123')
    #     self.assertTrue(u. is not None)
    #
    # def test_no_password_getter(self):
    #     u = Users(password = 'cat123')
    #     with self.assertRaises(AttributeError):
    #         u.password
    #
    # def test_password_verification(self):
    #     u = User(password = 'cat123')
    #     self.assertTrue(u.verify_password('cat123'))
    #     self.assertFalse(u.verify_password('cat321'))
    #     self.assertFalse(u.verify_password('dog123'))
    #
    # def test_password_salts_are_random(self):
    #     u = Users(password='cat123')
    #     u2 = Users(password='cat123')
    #     self.assertTrue(u.password_hash != u2.password_hash)

if __name__ == '__main__':
    unittest.main()
