#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_browser.py:

Pytests UI and browser testing.

Before running browser tests, ensure that the Selenium Chromedriver is placed in PATH (copy from test/chromedrivers to
venv/bin).
"""

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import multiprocessing
import sys
import random
import string
import pytest
from flask_testing import LiveServerTestCase
from flask import url_for

from urllib.request import urlopen
import urllib3
from selenium.webdriver.common.keys import Keys

letters = string.ascii_lowercase
# Set up random user
test_user_first_name = "Test"
test_user_last_name = ''.join(random.choice(letters) for i in range(5))
test_user_last_name = "User"
test_user_email = test_user_last_name + '@email.com'
test_user_password = 'cat1234'


def test_homepage_link_texts(test_client, session, browser, live_server):

    index_url = url_for('main.index', _external=True)

    browser.get(index_url)
    signup_link = browser.find_element_by_id('signup-link')
    assert signup_link.text == 'Sign up'
    about_link = browser.find_element_by_id(('about-link'))
    assert about_link.text == 'About'
    login_link = browser.find_element_by_id('login-link')
    assert login_link.text == 'Log in'


def test_simple_search(test_client, session, browser, live_server):

    index_url = url_for('main.index', _external=True)

    browser.get(index_url)
    search_text = browser.find_element_by_css_selector('input')
    assert search_text.get_attribute('aria-label') == "Search"
    search_button = browser.find_element_by_css_selector('.btn.btn-primary.btn-outline-light')
    assert search_button.text == 'Search'
    search_text.send_keys('cabbage')
    search_button.click()


# def test_user_signup(test_client, session, browser, live_server):
#
#     index_url = url_for('main.index', _external=True)
#     signup_url = url_for('auth.signup', _external=True)
#
#     browser.get(signup_url)
#     form_first_name = browser.find_element_by_id('signup_first_name')
#     form_last_name = browser.find_element_by_id('signup_last_name')
#     form_email = browser.find_element_by_id('signup_email')
#     form_password = browser.find_element_by_id('signup_password')
#     form_confirm = browser.find_element_by_id('signup_confirm')
#     form_submit = browser.find_element_by_id("submit_button")
#
#     form_first_name.send_keys(test_user_first_name)
#     form_last_name.send_keys(test_user_last_name)
#     form_email.send_keys(test_user_email)
#     form_password.send_keys(test_user_password)
#     form_confirm.send_keys(test_user_password)
#     form_submit.click()
#
#     assert browser.find_element_by_css_selector(
#         '.alert.alert-success.list-unstyled').text == '×\nYou are now a registered user!'
#
#     browser.get(index_url)
#     links = browser.find_elements_by_css_selector('a')
#     loggedin = False
#     for link in links:
#         if link.text == 'Account':  # Find if 'Account' is in navbar links to assure user is logged in.
#             loggedin = True
#         else:
#             pass
#     assert loggedin == True
#
#
# def test_user_signup_fails_if_email_already_registered(test_client, session, user, browser, live_server):
#     # URL = MEALTIME_URL
#     # signup_url = URL + '/signup/'
#
#     signup_url = url_for('auth.signup', _external=True)
#     browser.get(signup_url)
#
#     form_first_name = browser.find_element_by_id('signup_first_name')
#     form_last_name = browser.find_element_by_id('signup_last_name')
#     form_email = browser.find_element_by_id('signup_email')
#     form_password = browser.find_element_by_id('signup_password')
#     form_confirm = browser.find_element_by_id('signup_confirm')
#     form_submit = browser.find_element_by_id("submit_button")
#
#     form_first_name.send_keys("Any")
#     form_last_name.send_keys("Name")
#     form_email.send_keys('user@test.com')  # Email that has already been registered in conftest
#     form_password.send_keys("any_password")
#     form_confirm.send_keys("any_password")
#     form_submit.click()
#
#     assert browser.current_url == signup_url
#     assert browser.find_element_by_class_name('help-block').text == 'An account is already registered with this email.'
#
#
# def test_user_can_add_and_view_favourite_recipes(test_client, db, user, browser, live_server):
#     ###USER LOGS IN (ESSENTIALLY SAME AS ABOVE METHOD APART FROM LAST TWO LINES)
#     # URL = MEALTIME_URL
#
#     URL = url_for('main.index', _external=True)
#
#     browser.get(URL)
#     login = browser.find_element_by_id('login-link')
#     login.click()
#     assert browser.current_url == URL + 'login/'
#
#     form_email = browser.find_element_by_id('login-email')  ########THIS MIGHT NOT WORK IN VIRTUAL ENVIRONMENT -> LOGIN WITH DETAILS SAVED IN REAL DB, LIKE email = d@w.com, pword = 123456
#     form_password = browser.find_element_by_id('login-password')
#     form_submit = browser.find_element_by_css_selector('.btn.btn-primary')
#     form_email.send_keys('user@test.com')
#     form_password.send_keys('cat123')
#     form_submit.click()
#
#     # USER SEARCHES FOR CABBAGE
#     search_term = 'cabbage'
#     search_text = browser.find_element_by_css_selector('input')
#     assert search_text.get_attribute('aria-label') == "Search"
#     search_button = browser.find_element_by_css_selector('.btn.btn-primary.btn-outline-light')
#     print(browser.current_url)
#     assert search_button.text == 'Search'
#     search_text.send_keys(search_term)
#     search_button.click()
#     assert search_term in browser.current_url
#
#     # USER ADDS CABBAGE TO FAVOURITES
#     favourites = browser.find_elements_by_xpath('//button[text()="Add Favourite"]')
#     selected = random.randint(0, len(favourites)-1)
#     selected_tag = favourites[selected].get_attribute("id")
#     selected_id = selected_tag.replace('fav', '')
#     favourites[selected].click()
#     assert "Added" and "to favourites!" in browser.find_elements_by_class_name("toast-message")[0].text
#
#     # USER CHECKS CABBAGE IS IN FAVOURITES
#     fav_button = browser.find_element_by_id('favourites-link')
#     fav_button.click()
#     assert browser.current_url == URL + '/favourites'
#     body = browser.find_element_by_css_selector('body')
#     favourite_recipe = body.find_elements_by_css_selector('a')
#     added = False
#     for rec in favourite_recipe:
#         print(rec.get_attribute('href'))
#         if rec.get_attribute('href').replace(URL+'/recipe/', '') == selected_id:
#             added = True
#     assert added == True
