"""Flask config class."""
from os.path import dirname, abspath, join


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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(CWD, 'db/mealtime.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    # The following are fictitious details for a MySQL server database! Included to illustrate the syntax.
    DB_SERVER = '192.168.19.32'
    SQLALCHEMY_DATABASE_URI = 'sqlite://user@{}/foo'.format(DB_SERVER)
    DEBUG = False
    TESTING = False


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    #  To allow forms to be submitted from the tests without the CSRF token
    WTF_CSRF_ENABLED = False


class DevConfig(Config):
    DEBUG = True


app_config = {
    'development': DevConfig,
    'production': ProdConfig,
    'testing': TestConfig
}
