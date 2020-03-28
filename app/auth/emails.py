#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/auth/emails.py:

This file includes sample

The emails are not used in the final deliverable. However, we have kept it in the final submission as it is a potential
future requirement.
"""
__authors__ = "Ethan Low, Danny Wallis, and Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import mail

from flask_mail import Message


# This code is adapted from the Miguel Grinberg Flask mega-tutorial.

# Title: The Flask Mega-Tutorial, Part XI: Email Support
# Author: Miguel Grinberg
# Date: 2014
# Availability: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support
# Accessed: 27 March 2020



def confirm_signup_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)