#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py:

Defining the configurations for the Mealtime Flask application, including production, development and test configs.
"""
__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

"""Flask config class."""
from os.path import dirname, abspath, join

"""Global project variables set up in config"""
RECIPES_PER_PAGE = 12  # For pagination
MIN_PW_LEN = 6
MAX_PW_LEN = 20
DIET_CHOICES = [(1, 'Classic'),
                (2, 'Pescatarian'),
                (3, 'Vegetarian'),
                (4, 'Vegan')]
ALLERGY_CHOICES = [(1, 'Dairy-free'),
                   (2, 'Gluten-free'),
                   (3, 'Seafood-free'),
                   (4, 'Eggs-free'),
                   (5, 'Lupin-free'),
                   (6, 'Mustard-free'),
                   (7, 'Tree nuts-free'),
                   (8, 'Peanuts-free'),
                   (9, 'Sesame-free'),
                   (10, 'Soybeans-free'),
                   (11, 'Celery-free')]




class Config(object):
    """Set Flask base configuration"""
    SECRET_KEY = 'dfdQbTOExternjy5xmCNaA'

    # General Config
    DEBUG = False
    TESTING = False

    # Forms config
    WTF_CSRF_SECRET_KEY = 'f7Z-JN0ftel5Sp_TywHuxA'

    # Database config
    CWD = dirname(abspath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(CWD, 'db/mealtime.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # # EMAIL SETTINGS
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = 'secret_email'
    # MAIL_PASSWORD = 'secret_password'


class ProdConfig(Config):
    # The following are fictitious details for a MySQL server database! Included to illustrate the syntax.
    DB_SERVER = '192.168.19.32'
    SQLALCHEMY_DATABASE_URI = 'sqlite://user@{}/foo'.format(DB_SERVER)
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    DEBUG = True
    TESTING = True

    CWD = dirname(abspath(__file__))

    # Create a duplicate of the current database
    from shutil import copy
    src = join(CWD, 'db/mealtime.db') # current working db
    dst = join(CWD, 'db/mealtime_testing.sqlite') # destination for test db
    copy(src, dst) # copy (and overwrite) working db to test db

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dst
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # To allow forms to be submitted from the tests without the CSRF token
    WTF_CSRF_ENABLED = False


class DevConfig(Config):
    DEBUG = True


app_config = {
    'development': DevConfig,
    'production': ProdConfig,
    'testing': TestConfig
}
