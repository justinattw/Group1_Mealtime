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

from test.conftest import browser_signup

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

    index_url = url_for('main.index', _external=True)

    browser_signup(browser, browser_user_data)

    assert browser.find_element_by_css_selector(
        '.alert.alert-success.list-unstyled').text == '×\nYou are now a registered user!'

    browser.get(index_url)
    links = browser.find_elements_by_css_selector('a')
    loggedin = False
    for link in links:
        if link.text == 'Account':  # Find if 'Account' is in navbar links to assure user is logged in.
            loggedin = True
        else:
            pass
    assert loggedin == True