import os
import time
import unittest
import urllib.request
from os.path import join

from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from app import db, create_app

# Set test variables for test employee 1
test_user_first_name = "Test"
test_user_last_name = "Employee"
test_user_email = "employee1@email.com"
test_user_password = "test1234"


class TestBase(LiveServerTestCase):

    def create_app(self):
        from app import create_app
        app = create_app('config.TestConfig')
        return app

    def setUp(self):
        """Setup the test driver and create test users"""
        from app.models import Users
        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())

        db.session.commit()
        db.drop_all()
        db.create_all()

        self.user1 = Users(email=test_user_email, first_name=test_user_first_name, last_name=test_user_last_name)
        self.user1.set_password(test_user_password)

        # save users to database
        db.session.add(self.user1)
        db.session.commit()

    def tearDown(self):
        self.driver.quit()

    def test_server_is_up_and_running(self):
        response = urllib.request.urlopen(self.get_server_url())
        print(self.get_server_url())
        self.assertEqual(response.code, 200)

class CreateObjects(object):

     def login_test_user(self):
        """Log in as the test user"""
        login_link = self.get_server_url() + url_for('auth.login')
        self.driver.get(login_link)
        self.driver.find_element_by_id("email").send_keys(test_user_email)
        self.driver.find_element_by_id("password").send_keys(
            test_user_password)
        self.driver.find_element_by_id("submit").click()

class TestRegistration(TestBase):

    def test_signup_succeeds(self):
        """
        Test that a user can create an account using the signup form if all fields are filled out correctly, and that
        they will be redirected to the index page
        """

        # Click signup menu link
        self.driver.find_element_by_id("auth.signup").click()
        time.sleep(1)

        # Test person
        first_name = "Tester"
        last_name = "User"
        email = "tester@mail.com"
        password = "test123123"
        confirm = "test123123"

        # Fill in registration form
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("first_name").send_keys(first_name)
        self.driver.find_element_by_id("last_name").send_keys(last_name)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("confirm").send_keys(confirm)
        self.driver.find_element_by_id("submit").click()
        self.driver.implicitly_wait(10)

        # Assert that browser redirects to index page
        self.assertIn(url_for('main.index'), self.driver.current_url)

        # Assert success message is flashed on the index page
        success_message = self.driver.find_element_by_class_name("alert-warning").text
        self.assertIn("You are now a registered user!", success_message)

if __name__ == '__main__':
    unittest.main()

