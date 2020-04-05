#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_main.py:

Pytests tests for Mealtime app models
"""
__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

from sqlalchemy import and_


# def test_register_user_model(test_client, user_data, db):
#     """
#     GIVEN a flask app
#     WHEN a user registers with valid user details
#     THEN user and default diet preference is added to database
#     """
#     test_client.post('/signup/', data=dict(
#         first_name=user_data['first_name'],
#         last_name=user_data['last_name'],
#         email=user_data['email'],
#         password=user_data['password'],
#         confirm=user_data['confirm']
#     ), follow_redirects=True)
#
#     from app.models import Users, UserDietPreferences
#     users_query = db.session.query(Users).filter(Users.email == user_data['email']).all()
#     user_diet_preference_query = db.session.query(Users) \
#         .join(UserDietPreferences) \
#         .filter(and_(Users.email == user_data['email'],
#                      UserDietPreferences.diet_type_id == 1)) \
#         .all()
#
#     assert users_query is not None
#     assert user_diet_preference_query is not None
