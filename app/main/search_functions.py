from app import db
from app.models import Recipes, RecipeAllergies, RecipeDietTypes

def search_function(search_term="",
                    diet_type=1,
                    celery_free=False,
                    gluten_free=False,
                    seafood_free=False,
                    eggs_free=False,
                    lupin_free=False,
                    mustard_free=False,
                    tree_nuts_free=False,
                    peanuts_free=False,
                    sesame_free=False,
                    soybeans_free=False,
                    dairy_free=False):

    allergies = []
    if celery_free:
        allergies.append(1)
    if gluten_free:
        allergies.append(2)
    if seafood_free:
        allergies.append(3)
    if eggs_free:
        allergies.append(4)
    if lupin_free:
        allergies.append(5)
    if mustard_free:
        allergies.append(6)
    if tree_nuts_free:
        allergies.append(7)
    if peanuts_free:
        allergies.append(8)
    if sesame_free:
        allergies.append(9)
    if soybeans_free:
        allergies.append(10)
    if dairy_free:
        allergies.append(11)

    # Query begins here
    # subquery: blacklist recipes if user have certain allergies
    blacklist = db.session.query(RecipeAllergies.recipe_id) \
        .filter(RecipeAllergies.allergy_id.in_(allergies)).distinct().subquery()
    # filter allergies with a left outer join, so that blacklisted recipes are not matched
    results = db.session.query(Recipes) \
        .outerjoin(blacklist, Recipes.recipe_id == blacklist.c.recipe_id) \
        .filter(blacklist.c.recipe_id == None) \
        .join(RecipeDietTypes, Recipes.recipe_id == RecipeDietTypes.recipe_id) \
        .filter(RecipeDietTypes.diet_type_id >= diet_type) \
        .filter(Recipes.recipe_name.contains(search_term)).all()

    return results
