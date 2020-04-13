#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/main/routes.py:

This document includes functions for email functionalities within the main route.
"""
__authors__ = "Ethan Low, Danny Wallis, and Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import mail

from flask import render_template
from flask_login import current_user
from flask_mail import Message


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject,
                  sender=sender,
                  recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def send_grocery_list_email(mealplan_id, grocery_list):

    send_email(f'[Mealtime] Your grocery shopping list for Mealplan {mealplan_id}',
               sender=('Mealtime', 'comp0034mealtime@gmail.com'),
               recipients=[current_user.email],
               html_body=render_template('email/send_grocery_list_email.html',
                                         user=current_user, mealplan_id=mealplan_id, grocery_list=grocery_list))