#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/main/email.py:

This document includes functions for email functionalities within the main route.
"""
__authors__ = "Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Justin Wong"]
__status__ = "Development"

from app import mail

from flask import render_template
from flask_login import current_user
from flask_mail import Message


def send_email(subject, sender, recipients, html_body):
    """


    :param subject: Subject of email
    :param sender: Sender (Mealtime)
    :param recipients: recipient email address(es)
    :param html_body:
    """
    msg = Message(subject,
                  sender=sender,
                  recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def send_grocery_list_email(mealplan_id, grocery_list):
    """
    Uses send_email function to

    :param mealplan_id: for which meal plan
    :param grocery_list:
    :return:
    """
    send_email(f'[Mealtime] Your grocery shopping list for Mealplan {mealplan_id}',
               sender=('Mealtime', 'comp0034mealtime@gmail.com'),
               recipients=[current_user.email],
               html_body=render_template('email/send_grocery_list_email.html',
                                         user=current_user, mealplan_id=mealplan_id, grocery_list=grocery_list))
