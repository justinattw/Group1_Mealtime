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

from selenium.webdriver.common.keys import Keys

# MEALTIME_LOCALHOST_URL = 'http://127.0.0.1:5000'
MEALTIME_LOCALHOST_URL = 'localhost:5000'
# MEALTIME_LOCALHOST_URL = 'https://comp0034-mealtime.herokuapp.com'

#
# def test_driver_setup(browser):
#
#     URL = 'https://www.duckduckgo.com'
#     PHRASE = 'panda'
#
#     browser.get(URL)
#
#     search_input = browser.find_element_by_id('search_form_input_homepage')
#     search_input.send_keys(PHRASE + Keys.RETURN)
#
#     link_divs = browser.find_elements_by_css_selector('#links > div')
#     assert len(link_divs) > 0
#
#     xpath = f"//div[@id='links']//*[contains(text(), '{PHRASE}')]"
#     results = browser.find_elements_by_xpath(xpath)
#     assert len(results) > 0
#
#     search_input = browser.find_element_by_id('search_form_input')
#     assert search_input.get_attribute('value') == PHRASE


def test_driver_setup(test_client, browser):

    URL = MEALTIME_LOCALHOST_URL
    PHRASE = 'recipe'

    browser.get(URL)

    signup_link = browser.find_element_by_id('signup-link')
    print(signup_link.text)
    #search_input.send_keys(PHRASE + Keys.RETURN)

    # link_divs = browser.find_elements_by_css_selector('#links > div')
    # assert len(link_divs) > 0

    #xpath = f"//div[@id='links']//*[contains(text(), '{PHRASE}')]"
    #results = browser.find_elements_by_xpath(xpath)
    #assert len(results) > 0
    #
    # search_input = browser.find_element_by_id('search_form_input')
    # assert search_input.get_attribute('value') == PHRASE


def test_mealtime_index(test_client, browser):

    browser.get(MEALTIME_LOCALHOST_URL)
    # browser.implicitly_wait(100000000)
    pass