from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    user_type = db.Column(db.String(10), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": user_type
    }

    def __repr__(self):
        return "User email %s" % self.email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Student(User):
    __tablename__ = 'student'
    id = db.Column(None, db.ForeignKey('user.id'), primary_key=True)
    student_ref = db.Column(db.Integer)
    grades = db.relationship('Grade', backref='students')

    __mapper_args__ = {"polymorphic_identity": "student"}

    def __repr__(self):
        return '<Student ID: {}, name: {}>'.format(self.student_ref, self.name)


class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(None, db.ForeignKey('user.id'), primary_key=True)
    teacher_ref = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text)
    courses = db.relationship('Course', backref='teachers')

    __mapper_args__ = {"polymorphic_identity": "teacher"}

    def __repr__(self):
        return '<Teacher {} {}>'.format(self.teacher_ref, self.title, self.name)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=False)
    grades = db.relationship('Grade', backref='courses')

    def __repr__(self):
        return '<Course {}>'.format(self.code, self.name)


class Grade(db.Model):
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey(Course.id), nullable=False, primary_key=True)
    grade = db.Column(db.Text)

    def __repr__(self):
        return '<Grade {}>'.format(self.grade)


###################################################################################################
"""
MEALTIME DB MODELS.PY
For entity relationship diagram, see: https://www.lucidchart.com/invitations/accept/a9b31da9-ee84-4aca-8e64-996f781f17b7
"""

# class User(UserMixin, db.Model):
#     __tablename__ = "user"
#     id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#
#     first_name = db.Column(db.Text)
#     last_name = db.Column(db.Text)
#     email = db.Column(db.Text, unique=True, nullable=False)
#     password = db.Column(db.Text)
#
#     __mapper_args__ = {
#         "polymorphic_identity": "user",
#         "polymorphic_on": user_type
#     }
#
#     def __repr__(self):
#         return f'<User id {self.id} email {self.email}>'
#
#     def set_password(self, password):
#         self.password = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password, password)
#
#
# class DietPreferences(db.Model):
#     # Do we actually need the primary id? we could just use user_id
#     diet_preference_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
#     # TODO
#     # diet_preference =
#
#     def __repr__(self):
#         return f'<Diet Preference for user {self.user_id}>'
#
#
# class UserAllergies(db.Model):
#     # Do we actually need the primary id? we could just use user_id
#     user_allergies_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False
#                         )
#     shellfish_free = db.Column(db.Boolean, nullable=False, default=False)
#     fish_free = db.Column(db.Boolean, nullable=False, default=False)
#     gluten_free = db.Column(db.Boolean, nullable=False, default=False)
#     dairy_free = db.Column(db.Boolean, nullable=False, default=False)
#     peanut_free = db.Column(db.Boolean, nullable=False, default=False)
#     soy_free = db.Column(db.Boolean, nullable=False, default=False)
#     egg_free = db.Column(db.Boolean, nullable=False, default=False)
#     sesame_free = db.Column(db.Boolean, nullable=False, default=False)
#     mustard_free = db.Column(db.Boolean, nullable=False, default=False)
#
#     def __repr__(self):
#         return f'<User Allergies for user {self.user_id}>'
#
#
# class Mealplans(db.Model):
#     mealplan_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     # There can be many of the same users in this table
#     user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, primary_key=True)
#
#     # what time was the mealplan created at?
#     # the most recent mealplan is set as active, until user creates another mealplan
#     # format in yyyy-MM-dd HH:mm:ss. use parameterised query.
#     created_at = db.Column(db.Text, nullable=False)
#
#     def __repr__(self):
#         return f'<Meal plan {self.mealplan_id}, created by user {self.user_id} at {self.created_at}>'
#
#
# class MealplanRecipes(db.Model):
#     mealplan_id = db.Column(db.Integer, db.ForeignKey(Mealplans.mealplan_id), primary_key=True, nullable=False)
#     recipe_id = db.Column(db.Integer, db.ForeignKey(Users.id), primary_key=True, nullable=False)
#
#     servings = db.Column(db.Integer, default=2)
#
#     def __repr__(self):
#         return f'<Mealplan {self.mealplan_id} recipe {self.recipe_id}>'
#
#
# class Recipes(db.Model):
#     recipe_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#
#     recipe_name = db.Column(db.Text, nullable=False)
#     recipe_photo = db.Column(db.Text)
#
#     def __repr__(self):
#         return f'<Recipe {self.recipe_id}, name {self.recipe_name}>'
#
#
# class RecipeIngredients(db.Model):
#     recipe_ingredient_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), nullable=False)
#
#     ingredient = db.Column(db.Text, nullable=False)
#     amount = db.Column(db.Integer, nullable=False)
#     unit = db.Column(db.Text)
#
#     def __repr__(self):
#         return f'<Recipe ingredient {self.recipe_ingredient_id}?'
#
#
# class NutritionValues(db.Model):
#     """
#     Units:
#     - Calories (kcal)
#     - Fat (g)
#     - Saturates (g)
#     - Carbs (g)
#     - Sugar (g)
#     - Fibre (g)
#     - Protein (g)
#     - Salt (g)
#     """
#     nutrition_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), nullable=False)
#
#     calories = db.Column(db.Integer)
#     fats = db.Column(db.Integer)
#     saturatess = db.Column(db.Integer)
#     carbs = db.Column(db.Integer)
#     sugars = db.Column(db.Integer)
#     fibres = db.Column(db.Integer)
#     proteins = db.Column(db.Integer)
#     salts = db.Column(db.Integer)
#
#     def __repr__(self):
#         return f'<Nutrition values for recipe {self.recipe_id}>'

