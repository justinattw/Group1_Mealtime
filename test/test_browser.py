#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_browser.py:

Pytests UI and browser testing.

Before running browser tests, ensure that the Selenium Chromedriver is placed in PATH (copy from test/chromedrivers to
venv/bin).
"""
from flask_testing import LiveServerTestCase
from flask import url_for

from urllib.request import urlopen
import urllib3

__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

from selenium.webdriver.common.keys import Keys



MEALTIME_URL = 'localhost:5000'

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




def test_homepage_link_texts(test_client, browser, live_server):

    browser.get(url_for('main.index', _external=True))

    signup_link = browser.find_element_by_id('signup-link')
    assert signup_link.text == 'Sign up'
    about_link = browser.find_element_by_id(('about-link'))
    assert about_link.text == 'About'
    login_link = browser.find_element_by_id('login-link')
    assert login_link.text == 'Log in'



    # def test_all_links(browser):  #checks that all the links actually go somewhere
    #     URL = MEALTIME_LOCALHOST_URL
    #     browser.get(URL)
    #     links = browser.find_elements_by_css_selector('a')
    #     assert len(links) > 0  # make sure there are links
    #     linker = []
    #     all_links = []
    #     for link in links:
    #         linker.append(link.get_attribute('href'))  #saves links texts as array to avoid StaleElementReference
    #
    #     checked = []
    #     while len(checked) != len(linker):
    #         for l in linker:
    #             print(l)
    #             if MEALTIME_LOCALHOST_URL not in l: #Don't check sites that arent part of internal website, like GitHub or other external links
    #                 pass
    #             else:
    #                 if l not in checked:
    #                     checked.append(l)
    #                     browser.get(str(l)) #ensures all links can be followed
    #                     links = browser.find_elements_by_css_selector('a')
    #                     for link in links:
    #                         linker.append(link.get_attribute('href'))
    #                 linker = list(set(linker))

    #
    # def test_simple_search(self, browser):  #checks that the value searched is in the url
    #     URL = MEALTIME_LOCALHOST_URL
    #     browser.get(URL)
    #     search_text = browser.find_element_by_css_selector('input')
    #     assert search_text.get_attribute('aria-label') == "Search"
    #     search_button = browser.find_element_by_css_selector('.btn.btn-primary.btn-outline-light')
    #     assert search_button.text == 'Search'
    #     search_text.send_keys('cabbage')
    #     search_button.click()
    #
    # def test_user_login(self, browser):
    #     URL = MEALTIME_LOCALHOST_URL
    #     signup = 'http://127.0.0.1:5000/signup/'
    #     browser.get(signup)
    #     form_first_name = browser.find_element_by_id('signup_first_name')
    #     form_last_name = browser.find_element_by_id('signup_last_name')
    #     form_email = browser.find_element_by_id('signup_email')
    #     form_password = browser.find_element_by_id('signup_password')
    #     form_confirm = browser.find_element_by_id('signup_confirm')
    #     form_submit = browser.find_element_by_id("submit_button")
    #
    #     test_user_first_name = "A"
    #     test_user_last_name = "A"
    #     test_user_email = "A@email.com"
    #     test_user_password = "test12334"
    #
    #     form_first_name.send_keys(test_user_first_name)
    #     form_last_name.send_keys(test_user_last_name)
    #     form_email.send_keys(test_user_email)
    #     form_password.send_keys(test_user_password)
    #     form_confirm.send_keys(test_user_password)
    #     form_submit.click()
    #
    #     browser.get(URL)
    #     links = browser.find_elements_by_css_selector('a')
    #     print(browser.current_url)
    #     for link in links:
    #         print(link.text)

        # search_input.send_keys(PHRASE + Keys.RETURN)

        # link_divs = browser.find_elements_by_css_selector('#links > div')
        # assert len(link_divs) > 0

        # search_input = browser.find_element_by_id('search_form_input')
        # assert search_input.get_attribute('value') == PHRASE


