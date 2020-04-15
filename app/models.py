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

from flask_login import UserMixin
from flask_serialize import FlaskSerializeMixin
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash


class Users(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['Users']
    diet_preferences = relationship("UserDietPreferences", backref=backref("users", lazy="joined"))
    allergies = relationship("UserAllergies", backref=backref("users", lazy="joined"))
    favourite_recipes = relationship("UserFavouriteRecipes", backref=backref("users", lazy="joined"))
    mealplans = relationship("MealPlans", backref=backref("users", lazy="joined"))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class DietTypes(db.Model):
    __table__ = db.Model.metadata.tables['DietTypes']

    @property
    def serialize(self):
        return self.diet_name


class UserDietPreferences(db.Model):
    __table__ = db.Model.metadata.tables['UserDietPreferences']
    diet_type = relationship("DietTypes", backref=backref("userdietpreferences", lazy="joined"), uselist=False)


class Allergies(db.Model):
    __table__ = db.Model.metadata.tables['Allergies']

    @property
    def serialize(self):
        return self.allergy_name


class UserAllergies(db.Model):
    __table__ = db.Model.metadata.tables['UserAllergies']
    allergy = relationship("Allergies", backref=backref("userallergies", lazy="joined"), uselist=False)


class UserFavouriteRecipes(db.Model):
    __table__ = db.Model.metadata.tables['UserFavouriteRecipes']


class Recipes(db.Model):
    __table__ = db.Model.metadata.tables['Recipes']
    ingredients = relationship("RecipeIngredients", backref=backref("recipes", lazy="joined"))
    instructions = relationship("RecipeInstructions", backref=backref("recipes", lazy="joined"))
    nutrition_values = relationship("NutritionValues", backref=backref("recipes", lazy="joined"), uselist=False)
    allergies = relationship("RecipeAllergies", backref=backref("recipes", lazy="joined"))
    diet_type = relationship("RecipeDietTypes", backref=backref("recipes", lazy="joined"))

    @property
    def serialize(self):
        return {'recipe_id': self.recipe_id,
                'recipe_name': self.recipe_name,
                'recipe_ingredients': [ing.serialize for ing in self.ingredients],
                'recipe_instructions': [ins.serialize for ins in self.instructions],
                'nutrition_values': self.nutrition_values.serialize,
                'recipe_allergies': [all.serialize for all in self.allergies],
                'diet_type': self.diet_type[0].serialize}


class RecipeIngredients(db.Model, FlaskSerializeMixin):
    __table__ = db.Model.metadata.tables['RecipeIngredients']

    @property
    def serialize(self):
        return {'recipe_ingredient_id': self.recipe_ingredient_id,
                'ingredient_name': self.ingredient}


class RecipeInstructions(db.Model):
    __table__ = db.Model.metadata.tables['RecipeInstructions']

    @property
    def serialize(self):
        return {'step_num': self.step_num,
                'step_description': self.step_description}


class RecipeAllergies(db.Model):
    __table__ = db.Model.metadata.tables['RecipeAllergies']
    allergy = relationship("Allergies", backref=backref("recipeallergies", lazy="joined"))

    @property
    def serialize(self):
        return {'allergy_id': self.allergy_id, 'allergy_name': self.allergy.serialize}


class RecipeDietTypes(db.Model):
    __table__ = db.Model.metadata.tables['RecipeDietTypes']
    diet = relationship("DietTypes", backref=backref("recipediettypes", lazy="joined"))

    @property
    def serialize(self):
        return self.diet.serialize


class NutritionValues(db.Model):
    __table__ = db.Model.metadata.tables['NutritionValues']

    @property
    def serialize(self):
        return {'recipe_id': self.recipe_id,
                'calories': self.calories,
                'fats': self.fats,
                'saturates': self.saturates,
                'carbs': self.carbs,
                'sugars': self.sugars,
                'fibres': self.fibres,
                'proteins': self.proteins,
                'salts': self.salts}


class MealPlans(db.Model):
    __table__ = db.Model.metadata.tables['MealPlans']
    mealplan_recipes = relationship("MealPlanRecipes", backref=backref("mealplans", lazy="joined"))


class MealPlanRecipes(db.Model):
    __table__ = db.Model.metadata.tables['MealPlanRecipes']
    recipe = relationship("Recipes", backref=backref("mealplanrecipes", lazy="joined"))
