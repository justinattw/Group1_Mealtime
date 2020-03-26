#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/main/auth.py:

This document sets up functions for email support of the Mealtime application.

This document is NOT referred to in the final submission of the COMP0034 Mealtime group project. It is kept in for
future scaling of the application.
"""
__authors__ = "Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

# from app import mail

from flask import render_template
from flask_mail import Message


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_passowrd_token()
    send_email('[Mealtime] Reset your password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
