#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/models.py:

This document creates SQLAlchemy models by referencing the pre-existing mealtime.db database (if non-existing db,
first run db/create_db.py)
For entity relationship diagram, see: https://www.lucidchart.com/invitations/accept/a9b31da9-ee84-4aca-8e64-996f781f17b7
"""
__authors__ = "Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt



class Users(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['Users']

    def __repr__(self):
        return f'<User id {self.id} email {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # def get_reset_password_token(self, expires_in=600):
    #     return jwt.encode(
    #         {'reset_password': self.id, 'exp': time() + expires_in},
    #         app.config['SECRET_KEY'], algorithm='HS256').encode('utf-8')
    #
    # @staticmethod
    # def verify_reset_password_token(token):
    #     try:
    #         id = jwt.decode(token, app.config['SECRET_KEY'],
    #                         algorithms=['HS256'])['reset_password']
    #     except:
    #         return
    #     return Users.query.get(id)


class DietTypes(db.Model):
    __table__ = db.Model.metadata.tables['DietTypes']


class UserDietPreferences(db.Model):
    __table__ = db.Model.metadata.tables['UserDietPreferences']


class Allergies(db.Model):
    __table__ = db.Model.metadata.tables['Allergies']


class UserAllergies(db.Model):
    __table__ = db.Model.metadata.tables['UserAllergies']


class Recipes(db.Model):
    __table__ = db.Model.metadata.tables['Recipes']


class RecipeIngredients(db.Model):
    __table__ = db.Model.metadata.tables['RecipeIngredients']


class RecipeInstructions(db.Model):
    __table__ = db.Model.metadata.tables['RecipeInstructions']


class NutritionValues(db.Model):
    __table__ = db.Model.metadata.tables['NutritionValues']


class MealPlans(db.Model):
    __table__ = db.Model.metadata.tables['MealPlans']


class MealPlanRecipes(db.Model):
    __table__ = db.Model.metadata.tables['MealPlanRecipes']


class RecipeAllergies(db.Model):
    __table__ = db.Model.metadata.tables['RecipeAllergies']


class RecipeDietTypes(db.Model):
    __table__ = db.Model.metadata.tables['RecipeDietTypes']

class UserFavouriteRecipes(db.Model):
    __table__ = db.Model.metadata.tables['UserFavouriteRecipes']
