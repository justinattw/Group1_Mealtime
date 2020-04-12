#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/init.py:

This document initialises the Flask application with configurations settings found in config.py. It initialises a Flask
object with a defined database and its associated class models (with SQLAlchemy).
"""
__authors__ = "Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from config import DevConfig

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

mail = Mail()


def page_not_found(e):
    return render_template('errors/404.html'), 404


def internal_server_error(e):
    return render_template('errors/500.html'), 500


def create_app(config_class=DevConfig):
    """
    Creates an application instance to run
    :return: A Flask object
    """
    app = Flask(__name__)
    Bootstrap(app)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)

    # app.config['MAIL_SERVER']='smtp.gmail.com'
    # app.config['MAIL_PORT']=587
    # app.config['MAIL_USE_SSL']=True
    # app.config['MAIL_PORT'] = 587
    # app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_USERNAME']='comp0034mealtime@gmail.com'
    # app.config['MAIL_PASSWORD'] = 'BASCsFinest'

    app.config.update(
        # EMAIL SETTINGS
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        # MAIL_PORT=587,
        # MAIL_USE_TSL=True
        MAIL_USERNAME='comp0034mealtime@gmail.com',
        MAIL_PASSWORD='BASCsFinest'
    )

    mail.init_app(app)

    with app.app_context():
        db.Model.metadata.reflect(db.engine)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    # Register Blueprints
    from app.main.routes import bp_main
    app.register_blueprint(bp_main)

    from app.auth.routes import bp_auth
    app.register_blueprint(bp_auth)

    from app.api.routes import bp_api
    app.register_blueprint(bp_api)

    return app
