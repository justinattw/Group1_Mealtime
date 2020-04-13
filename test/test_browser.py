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

from test.conftest import browser_signup, browser_login

from flask import url_for
import pytest
import random
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


def test_homepage_link_texts(test_client, db, session, browser, live_server):
    index_url = url_for('main.index', _external=True)

    browser.get(index_url)

    # Assert navbar is present
    signup_link = browser.find_element_by_id('signup-link')
    assert signup_link.text == 'Sign up'
    about_link = browser.find_element_by_id(('about-link'))
    assert about_link.text == 'About'
    login_link = browser.find_element_by_id('login-link')
    assert login_link.text == 'Log in'


def test_simple_search(test_client, db, session, browser, live_server):
    index_url = url_for('main.index', _external=True)

    browser.get(index_url)
    search_text = browser.find_element_by_css_selector('input')
    assert search_text.get_attribute('aria-label') == "Search"
    search_button = browser.find_element_by_css_selector('.btn.btn-primary.btn-outline-light')
    assert search_button.text == 'Search'
    search_text.send_keys('cabbage')
    search_button.click()

    # Assert the navbar is still present
    signup_link = browser.find_element_by_id('signup-link')
    assert signup_link.text == 'Sign up'
    about_link = browser.find_element_by_id(('about-link'))
    assert about_link.text == 'About'
    login_link = browser.find_element_by_id('login-link')
    assert login_link.text == 'Log in'


def test_user_signup(test_client, db, session, browser, live_server, browser_user_data):
    """
    GiVEN a Flask application and live test server
    WHEN user requests signup with valid details
    THEN user signup succeeds and user is logged in
    """
    index_url = url_for('main.index', _external=True)

    browser_signup(browser, browser_user_data)  # Signup user with user details

    assert browser.find_element_by_css_selector(
        '.alert.alert-success.list-unstyled').text == '×\nYou are now a registered user!'
    assert browser.current_url == index_url

    # browser.get(index_url)
    links = browser.find_elements_by_css_selector('a')
    loggedin = False
    for link in links:
        if link.text == 'Log out':  # Find if 'Log out' is in navbar links to assure user is logged in.
            loggedin = True
        else:
            pass
    assert loggedin == True

    """
    GiVEN a Flask application and live test server, user is signed up but logged out
    WHEN user requests signup previously registered details
    THEN user signup fails
    """
    logout = browser.find_element_by_id('logout-link')
    logout.click()  # First log out registered user

    browser_signup(browser, browser_user_data)  # Sign up user with previously registered details

    signup_url = url_for('auth.signup', _external=True)
    assert browser.current_url == signup_url
    assert browser.find_element_by_class_name('help-block').text == 'An account is already registered with this email.'


def test_user_can_login_after_registered(test_client, db, session, browser, live_server, browser_user_data):
    """
    GIVEN a Flask application and live test server, and user is registered
    WHEN user logs in with registered details
    THEN log in succeeds
    """

    index_url = url_for('main.index', _external=True)
    browser.get(index_url)

    login = browser.find_element_by_id('login-link')
    login.click()
    assert browser.current_url == url_for('auth.login', _external=True)

    browser_login(browser, browser_user_data)

    assert browser.find_element_by_css_selector(
        '.alert.alert-success.list-unstyled').text == '×\nLogged in successfully. Welcome, ' + browser_user_data[
               "first_name"] + '!'


@pytest.mark.parametrize("search_term", [('cabbage'), ('mango'), ('rice'), ('noodles')]) # ('mango')
def test_user_can_add_and_view_favourite_recipes(test_client, db, session, browser, live_server, browser_user_data,
                                                 search_term):
    """
    GIVEN a Flask application and live test server, and user is logged in
    WHEN user logs adds a recipe to favourites
    THEN recipe is added to favourites
    """
    index_url = url_for('main.index', _external=True)
    # browser_signup(browser, browser_user_data)
    browser_login(browser, browser_user_data)

    search_term = search_term  # User searches for parameterised searches

    search_text = browser.find_element_by_css_selector('input')
    assert search_text.get_attribute('aria-label') == "Search"
    search_button = browser.find_element_by_css_selector('.btn.btn-primary.btn-outline-light')
    assert search_button.text == 'Search'
    search_text.send_keys(search_term)
    search_button.click()
    assert search_term in browser.current_url

    # User adds recipe to favourites
    favourites = browser.find_elements_by_xpath('//button[text()="Add Favourite"]')

    selected = random.randint(0, len(favourites) - 1)
    selected_tag = favourites[selected].get_attribute("id")
    selected_id = selected_tag.replace('fav', '')
    element = browser.find_elements_by_xpath('//button[text()="Add Favourite"]')
    browser.execute_script("arguments[0].click();", element[selected])

    assert "Added" and "to favourites!" in browser.find_element_by_class_name("toast-message").text

    # User checks the added recipe is in favourites
    element = browser.find_element_by_id('favourites-link')
    browser.execute_script("arguments[0].click();", element)

    favourites_url = url_for('main.favourites', _external=True)
    assert browser.current_url == favourites_url

    body = browser.find_element_by_css_selector('body')
    favourite_recipe = body.find_elements_by_css_selector('a')
    added = False

    for rec in favourite_recipe:
        if rec.get_attribute('href').replace(index_url + 'recipe/', '') == selected_id:
            added = True
    assert added == True

    """
    GIVEN a Flask application and live test server, and user is logged in and recipe is added to favourites
    WHEN user logs unfavourites a recipe
    THEN recipe is removed from favourites
    """
    # User removes added recipe from favourites
    unselected_tag = 'un' + selected_tag
    element = browser.find_element_by_id(unselected_tag)
    browser.execute_script("arguments[0].click();", element)

    browser.get(browser.current_url)
    element = browser.find_element_by_id('favourites-link')

    # element_id = 'favourites-link'
    # ignored_exceptions=(NoSuchElementException, StaleElementReferenceException)
    # element = WebDriverWait(browser, 2, ignored_exceptions=ignored_exceptions) \
    #     .until(expected_conditions.presence_of_all_elements_located((By.ID, element_id)))

    browser.execute_script("arguments[0].click();", element)
    assert browser.current_url == favourites_url  # Checks that browser has navigated to favourites

    body = browser.find_element_by_css_selector('body')
    favourite_recipe = body.find_elements_by_css_selector('a')

    added = False
    for rec in favourite_recipe:
        if rec.get_attribute('href').replace(index_url + 'recipe/', '') == selected_id:
            added = True
    assert added == False
