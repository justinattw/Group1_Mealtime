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

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text)

    diet_preference = db.relationship('UserDietPreferences', backref='users')
    allergies = db.relationship('UserAllergies', backref='users')
    mealplans = db.relationship('MealPlans', backref='users')

    # Don't think we need this
    # __mapper_args__ = {
    #     "polymorphic_identity": "user",
    #     "polymorphic_on": user_type
    # }

    def __repr__(self):
        return f'<User id {self.id} email {self.email}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class DietTypes(db.Model):
    diet_type_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    diet_name = db.Column(db.Text)

    user_diet_preferences = db.relationship('UserDietPreferences', backref='diet_types')

    def __repr__(self):
        return f'<Diet type {self.diet_type_id}>'


class UserDietPreferences(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True, unique=True)
    diet_type_id = db.Column(db.Integer, db.ForeignKey(DietTypes.diet_type_id), primary_key=True)

    def __repr__(self):
        return f'<Diet preference {self.diet_preference_id} for user {self.user_id}>'


class Allergies(db.Model):
    allergy_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    allergy_name = db.Column(db.Text, nullable=False)

    user_allergies = db.relationship('UserAllergies', backref='allergies')
    recipe_allergies = db.relationship('RecipeAllergies', backref='allergies')

    def __repr__(self):
        return f'<Allergy {self.allergy_id}>'


class UserAllergies(db.Model):
    # Do we actually need the primary id? we could just use user_id
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    allergy_id = db.Column(db.Integer, db.ForeignKey(Allergies.allergy_id), primary_key=True)

    def __repr__(self):
        return f'<User allergy {self.allergy_id} for user {self.user_id}>'


class MealPlans(db.Model):
    mealplan_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # what time was the mealplan created at?
    # the most recent mealplan is set as active, until user creates another mealplan
    # format in yyyy-MM-dd HH:mm:ss. use parameterised query.
    created_at = db.Column(db.Text, nullable=False)

    mealplan_recipes = db.relationship('MealPlanRecipes', backref='mealplans')

    def __repr__(self):
        return f'<Meal plan {self.mealplan_id}, created by user {self.user_id} at {self.created_at}>'


class MealPlanRecipes(db.Model):
    mealplan_id = db.Column(db.Integer, db.ForeignKey(MealPlans.mealplan_id), primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Users.id), primary_key=True, nullable=False)

    selected_servings = db.Column(db.Integer, default=2)

    def __repr__(self):
        return f'<Mealplan {self.mealplan_id} recipe {self.recipe_id}>'


class Recipes(db.Model):
    recipe_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)

    recipe_name = db.Column(db.Text, nullable=False)
    photo = db.Column(db.Text)
    serves = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    prep_time = db.Column(db.Integer)
    total_time = db.Column(db.Integer)

    recipe_mealplans = db.relationship('MealPlanRecipes', backref='recipes')
    ingredients = db.relationship('RecipeIngredients', backref='recipes')
    nutrition_values = db.relationship('NutritionValues', backref='recipes')
    instructions = db.relationship('RecipeInstructions', backref='recipes')
    allergies = db.relationship('RecipeAllergies', backref='recipes')
    diet_type = db.relationship('RecipeDietTypes', backref='recipes')


    def __repr__(self):
        return f'<Recipe {self.recipe_id}, name {self.recipe_name}>'


class RecipeIngredients(db.Model):
    recipe_ingredient_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), nullable=False)

    ingredient = db.Column(db.Text, nullable=False)
    # amount = db.Column(db.Integer)
    # unit = db.Column(db.Text)

    def __repr__(self):
        return f'<Recipe ingredient {self.recipe_ingredient_id}?'


class NutritionValues(db.Model):
    nutrition_value_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), nullable=False)

    calories = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    saturatess = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    sugars = db.Column(db.Integer)
    fibres = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    salts = db.Column(db.Integer)

    def __repr__(self):
        return f'<Nutrition values for recipe {self.recipe_id}>'


class RecipeInstructions(db.Model):
    recipe_instruction_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), nullable=False)

    step_num = db.Column(db.Integer, nullable=False)
    step_description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Recipe {self.recipe_id} step {self.step_num}>'


class RecipeAllergies(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), primary_key=True, nullable=False)
    allergy_id = db.Column(db.Integer, db.ForeignKey(Allergies.allergy_id), primary_key=True, nullable=False)

    def __repr__(self):
        return f'<Recipe {self.recipe_id} allergy {self.allergy_id}>'


class RecipeDietTypes(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), primary_key=True, nullable=False, unique=True)
    diet_type_id = db.Column(db.Integer, db.ForeignKey(DietTypes.diet_type_id), primary_key=True, nullable=False)

    def __repr__(self):
        return f'<Recipe {self.recipe_id} diet type {self.diet_type_id}>'


# class Nutrition(db.Model):
#     nutrition_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     nutrition_name = db.Column(db.Text, unique=True, nullable=False)
#     unit = db.Column(db.Text)
#
#     def __repr__(self):
#         return f'<Nutrition {self.nutrition_id}>'

# class RecipeNutritionValues(db.Model):
#     recipe_id = db.Column(db.Integer, db.ForeignKey(Recipes.recipe_id), primary_key=True, nullable=False)
#     nutrition_id = db.Column(db.Integer, db.ForeignKey(Nutrition.nutrition_id), primary_key=True, nullable=False)
#     nutrition_value = db.Column(db.Float, nullable=False)
#
#     def __repr__(self):
#         return f'<Recipe {self.recipe_id} nutrition {self.nutrition_id}'
