"""
Author: Justin Wong
"""
from sqlalchemy import and_, desc
from app import db
from app.models import Users, Recipes, RecipeAllergies, RecipeDietTypes, NutritionValues, MealPlans, MealPlanRecipes, \
    RecipeIngredients


def search_function(search_term="", diet_type=1, allergy_list=[], min_cal=0, max_cal=1000):
    """
    This function accepts 5 parameters to find appropriate recipes according to user input (or default values)

    :param search_term: search term for recipe name
    :param diet_type: specified diet type
    :param allergy_list: list of allergies
    :param min_cal: minimum calorie
    :param max_cal: maximum calorie
    :return: an SQLAlchemy query of recipes matching the above parameters
    """

    # Subquery: blacklist recipes if user have certain allergies
    blacklist = db.session.query(RecipeAllergies.recipe_id) \
        .filter(RecipeAllergies.allergy_id.in_(allergy_list)).distinct().subquery()

    # Filter allergies with a left outer join on blacklist, so that blacklisted recipes are not matched
    results = db.session.query(Recipes) \
        .outerjoin(blacklist, Recipes.recipe_id == blacklist.c.recipe_id) \
        .filter(blacklist.c.recipe_id == None) \
        .join(RecipeDietTypes, Recipes.recipe_id == RecipeDietTypes.recipe_id) \
        .join(NutritionValues, Recipes.recipe_id == NutritionValues.recipe_id) \
        .filter(RecipeDietTypes.diet_type_id >= diet_type) \
        .filter(Recipes.recipe_name.contains(search_term)) \
        .filter(and_(NutritionValues.calories >= min_cal,
                     NutritionValues.calories <= max_cal)).all()

    return results


def generate_groceries_list(user_id, mealplan_id=None):
    """

    :param user_id: user details for which the grocery list should be generated
    :return:
    """
    if not mealplan_id:
        mealplan_id = db.session.Query(Users) \
            .join(MealPlans, Users.id == MealPlanRecipes.user_id) \
            .filter(Users.id == user_id) \
            .order_by(desc(MealPlans.mealplan_id)) \
            .limit(1) \
            .mealplan_id

    results = db.session.Query(Users) \
        .join(MealPlans, Users.id == MealPlanRecipes.user_id) \
        .join(MealPlanRecipes, MealPlans.mealplan_id == MealPlanRecipes.mealplan_id) \
        .join(RecipeIngredients, MealPlanRecipes.recipe_id == RecipeIngredients.recipe_id) \
        .filter(MealPlans.mealplan_id == mealplan_id)
