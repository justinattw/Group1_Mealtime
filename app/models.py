"""
Author: Justin Wong
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

"""
Create SQLAlchemy models by referencing the already created mealtime.sqlite database.
For entity relationship diagram, see: https://www.lucidchart.com/invitations/accept/a9b31da9-ee84-4aca-8e64-996f781f17b7
"""


class Users(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['Users']

    def __repr__(self):
        return f'<User id {self.id} email {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


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
