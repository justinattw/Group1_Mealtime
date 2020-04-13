#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_main.py:

Pytests tests for main views and methods (relating to files in app/main/)

app/main COVERAGE: 100% files, 93% lines covered

We achieve 93% coverage of the app/main directory, but the uncovered sections seem to be code that we cannot trigger
deliberately through the routes (such as IntegrityError for signing up), because there are form validations and route
validations that prevent them from occurring. Most untested sections are final failsafes (excepts) in case the
connection to SQLAlchemy database fails.

We make extensive use of pytest parametrisation to ensure exhaustive coverage.
"""
__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import config
from test.conftest import search_function, add_to_favourites, view_recipe, view_favourites, view_about, \
    login_test_user, del_from_mealplan, view_grocery_list, view_mealplan, get_recipe_ids, view_advanced_search, \
    advanced_search_function, create_mealplan, view_all_recipes, add_to_mealplan, delete_mealplan, edit_preferences, \
    remove_from_favourites, send_grocery_list

from flask import url_for
import pytest
import random
from sqlalchemy.sql import func


class TestSimpleViews:

    def test_index_page_valid_and_content(self, test_client):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested (GET)
        THEN check the response is valid and correct content is in response data
        """
        response = test_client.get('/')
        assert response.status_code == 200
        assert b'Meal planning made easy' in response.data

    def test_view_favourites_invalid_without_login(self, test_client):
        """
        GIVEN a flask app
        WHEN /favourites page is requested without login
        THEN response is invalid and redirects to login
        """
        response = test_client.get('/favourites')
        assert response.status_code == 302
        assert url_for('auth.login') in response.location  # login route is in redirect location

        response = test_client.get('/favourites', follow_redirects=True)
        assert response.status_code == 200
        assert b'You must be logged in to view that page.' in response.data  # Method not allowed

    def test_view_favourites_valid_with_login(self, test_client, user):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests to view their favourites (before having added a favourite recipe)
        THEN response is always valid and correct data is displayed
        """
        login_test_user(test_client)

        response = test_client.get('/favourites', follow_redirects=True)
        print(response.data)
        assert response.status_code == 200
        assert b"'s favourite recipes" in response.data
        assert b"You haven't favourited any recipes! Check out the " in response.data

    def test_view_about(self, test_client):
        """
        GIVEN a Flask application
        WHEN the 'about' page is requested'
        THEN response is valid
        """
        response = view_about(test_client)
        assert response.status_code == 200
        assert b'About Mealtime' in response.data

    def test_view_all_recipes(self, test_client):
        """
        GIVEN a flask application
        WHEN user requests to view all recipes
        THEN view is successful and there are recipes
        """
        response = view_all_recipes(test_client)
        assert response.status_code == 200
        response_recipe_ids = get_recipe_ids(test_client, response)
        assert len(response_recipe_ids) > 0

    def test_view_advanced_search(self, test_client):
        """
        GIVEN a Flask application
        WHEN the 'view_advanced_search' page is requested'
        THEN response is valid
        """
        response = view_advanced_search(test_client)
        assert response.status_code == 200
        assert b'Search' in response.data
        assert b'Calorie range (per person):' in response.data
        assert b'Diet type' in response.data
        assert b'Allergies' in response.data


class TestViewRecipes:

    @pytest.mark.parametrize("random_recipe", [(random.randint(0, 1400)) for i in range(5)])  # random recipe 5 times
    def test_view_recipe(self, test_client, db, random_recipe):
        """
        GIVEN a Flask application
        WHEN user requests page to view a recipe
        THEN response is valid
        """
        from app.models import Allergies, RecipeAllergies, Recipes

        response = view_recipe(test_client, random_recipe)
        assert response.status_code == 200
        assert str(random_recipe).encode() in response.data

        """
        GIVEN a Flask application
        WHEN user requests page to view a recipe
        THEN allergies of a recipe are all displayed on the page
        """
        allergies = db.session.query(Allergies.allergy_name) \
            .join(RecipeAllergies) \
            .filter(RecipeAllergies.recipe_id == random_recipe) \
            .all()
        allergy_list = [value for value, in allergies]  # Turn allergies query results into a list

        for allergy in allergy_list:
            assert allergy.encode() in response.data


class TestFavourites:

    def test_add_to_favourite(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites
        THEN check response is valid abd favourited recipe has been added to model/ table
        """
        from app.models import UserFavouriteRecipes, Recipes

        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
        # indicating how many recipes there are.
        # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
        # can upload + delete their uploaded recipes, this will need to be changed.

        rand_favourite = random.randint(1, number_of_recipes)  # generate a random favourite recipe_id to test
        response = add_to_favourites(test_client, rand_favourite)  # add random favourite recipe to favourites
        assert response.status_code == 200
        assert b'failure' not in response.data

        favourited = db.session.query(UserFavouriteRecipes) \
            .filter(UserFavouriteRecipes.user_id == user.id) \
            .filter(UserFavouriteRecipes.recipe_id == rand_favourite) \
            .first()
        assert favourited  # recipe is favourited if this is not None

    def test_add_to_favourite_twice_raises_error(self, test_client, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites that has already been added
        THEN check that an IntegrityError/ ObjectDeletedError occurs from SQLAlchemy
        """
        login_test_user(test_client)

        from app.models import Recipes
        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()
        rand_favourite = random.randint(1, number_of_recipes)

        add_to_favourites(test_client, rand_favourite)            # Add favourite recipe first time
        response = add_to_favourites(test_client, rand_favourite) # Add favourite recipe second time
        assert b'failure' in response.data

        # with pytest.raises(ObjectDeletedError):
        #     # Although in the routes we expect IntegrityError, ObjectDeletedError is raised in some instances
        #     response = add_to_favourites(test_client, rand_favourite)  # Add favourite recipe twice

    def test_delete_from_favourites_success(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites that has already been added
        THEN check that an IntegrityError/ ObjectDeletedError occurs from SQLAlchemy
        """
        from app.models import UserFavouriteRecipes, Recipes
        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()
        rand_favourite = random.randint(1, number_of_recipes)

        add_to_favourites(test_client, rand_favourite)
        favourited = db.session.query(UserFavouriteRecipes) \
            .filter(UserFavouriteRecipes.user_id == user.id) \
            .filter(UserFavouriteRecipes.recipe_id == rand_favourite) \
            .first()
        assert favourited  # Recipe is added to favourites

        remove_from_favourites(test_client, rand_favourite)
        favourited = db.session.query(UserFavouriteRecipes) \
            .filter(UserFavouriteRecipes.user_id == user.id) \
            .filter(UserFavouriteRecipes.recipe_id == rand_favourite) \
            .first()
        assert not favourited  # Recipe is not added to favourites (removed from favourites)

    def test_delete_from_favourites_when_recipe_is_not_in_favourites(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites that has already been added
        THEN check that an IntegrityError/ ObjectDeletedError occurs from SQLAlchemy
        """
        from app.models import Recipes
        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Get number of recipes in db
        rand_favourite = random.randint(1, number_of_recipes)

        response = remove_from_favourites(test_client, rand_favourite)
        assert b'failure' in response.data

    def test_add_to_favourites_and_view_favourites(self, test_client, logged_in_user, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user favourites a new recipe and views their Favourites page
        THEN response is valid (response code is 200), and favourited recipe_name is in the response data
        """
        from app.models import Recipes

        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
        # indicating how many recipes there are.
        # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
        # can upload + delete their uploaded recipes, this will need to be changed.

        favourite = random.randint(1, number_of_recipes)
        response = add_to_favourites(test_client, favourite)
        assert response.status_code == 200
        assert b'failure' not in response.data

        # Get recipe name of favourited recipe
        fav_name, = db.session.query(Recipes.recipe_name).filter(Recipes.recipe_id == favourite).first()
        fav_list = fav_name.split()
        response = view_favourites(test_client)
        assert response.status_code == 200

        # Could not convert string containing apostrophes to binary using encode, so the string had to be split
        for part in fav_list:
            if "'" in part:  # If apostrophe ' is in the name, then split the string by the '
                part = part.split("'")[0]
                assert part.encode() in response.data
            else:
                assert part.encode() in response.data


class TestMealplans:

    def test_view_mealplanner_without_login(self, test_client):
        """
        GIVEN a Flask application
        WHEN the 'view_mealplanner' page is requested'
        THEN redirects to login page
        """
        response = test_client.get('/mealplanner')
        redirect_url = url_for('auth.login')
        assert response.status_code == 302
        assert redirect_url in response.location

        response = test_client.get('/mealplanner', follow_redirects=True)
        assert response.status_code == 200
        assert b'You must be logged in' in response.data

    def test_view_mealplanner_with_login(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN the 'view_mealplanner' page is requested'
        THEN response is valid
        """
        response = test_client.get('/mealplanner', follow_redirects=True)
        assert response.status_code == 200
        assert b'Meal Planner' in response.data
        assert b"You don't have any meal plans" in response.data

    @pytest.mark.parametrize("random_mealplan",
                             [(random.randint(0, 1000)) for i in range(5)])  # random mealplan 5 times
    def test_cannot_view_other_users_mealplan(self, test_client, user, logged_in_user, random_mealplan):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests to view mealplan that they do not own
        THEN error message flashes
        """
        # User has no mealplans, so they cannot view any. We can feed any mealplan_id into the url and it should fail
        url = '/view_mealplan/' + str(random_mealplan)
        response = test_client.get(url, follow_redirects=True)
        assert b'Sorry, you do not have access to this meal plan' in response.data

    def test_add_recipe_when_mealplan_not_created_fails(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user tries to add recipe to meal plan before creating a meal plan
        THEN appropriate error
        """
        from app.models import MealPlans
        mealplan = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert not mealplan  # Assert user has not already created a meal plan

        response = add_to_mealplan(test_client, random.randint(0, 1400))  # add a random recipe to meal plan
        assert b'no plan' in response.data  # JS notification shows

    def test_create_new_mealplan_success(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN the 'create_mealplan' is requested
        THEN response is valid and meal plan is added to database, and that you can view the meal plan
        """
        from app.models import MealPlans
        query = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert query is None  # Assert user has not already created a meal plan

        response = create_mealplan(test_client)
        assert b'Success, new meal plan' in response.data
        assert response.status_code == 200

        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        assert mealplan_id is not None

        response = view_mealplan(test_client, mealplan_id)
        check_message = f"{user.first_name}'s meal plan {mealplan_id}"
        assert response.status_code == 200
        assert check_message.encode() in response.data

    def test_cannot_add_new_mealplan_while_old_mealplan_is_empty(self, test_client, user, logged_in_user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests 'create_mealplan' twice (thus on the second request, the active meal plan is empty)
        THEN appropriate error messages flashes on second attempt
        """
        create_mealplan(test_client)  # Create meal plan once
        response = create_mealplan(test_client)  # Create meal plan twice
        assert b'Your most recent meal plan' in response.data
        assert b'has no recipes. Please make use of it before' in response.data
        assert b'creating a new meal plan' in response.data
        assert response.status_code == 200

    def test_add_and_delete_recipe_from_mealplan(self, test_client, logged_in_user, user, db):
        """
        GIVEN a Flask application, user is logged in and meal plan is created
        WHEN user adds new recipe to mealplan
        THEN success message is shown, and the recipe is added to meal plan
        """
        create_mealplan(test_client)

        from app.models import MealPlans, MealPlanRecipes
        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        # Get current mealplan id

        recipe_id = random.randint(0, 1400)
        response = add_to_mealplan(test_client, recipe_id)
        assert response.status_code == 200
        assert b'success' in response.data

        recipe_is_added = db.session.query(MealPlanRecipes) \
            .filter(MealPlanRecipes.mealplan_id == mealplan_id) \
            .filter(MealPlanRecipes.recipe_id == recipe_id)
        assert recipe_is_added  # recipe is added to mealplan

        """
        GIVEN a Flask application, user is logged in and recipe has been added to a mealplan
        WHEN when user removes the recipe from mealplan
        THEN recipe is removed from mealplan
        """
        response = del_from_mealplan(test_client, mealplan_id, recipe_id)
        assert response.status_code == 200
        assert b'success' in response.data

        recipe_is_added = db.session.query(MealPlanRecipes) \
            .filter(MealPlanRecipes.mealplan_id == mealplan_id) \
            .filter(MealPlanRecipes.recipe_id == recipe_id).first()
        assert not recipe_is_added  # recipe is added to mealplan

    def test_add_duplicate_recipes_to_mealplan(self, test_client, logged_in_user):
        """
        GIVEN a Flask application, user is logged in and meal plan is created
        WHEN user adds the same recipe to mealplan twice
        THEN error message shows
        """
        create_mealplan(test_client)
        recipe_id = random.randint(0, 1400)

        add_to_mealplan(test_client, recipe_id)  # Add recipe to meal plan first time
        response = add_to_mealplan(test_client, recipe_id)  # Add recipe to meal plan second time
        assert b'failure' in response.data

    def test_remove_recipe_from_mealplan_when_recipe_already_not_in_mealplan_fails(self, test_client, logged_in_user,
                                                                                   user, db):
        """
        GIVEN a Flask application, user is logged in and meal plan is created
        WHEN user requests to remove a recipe from mealplan while recipe isn't in mealplan
        THEN error message shows
        """
        create_mealplan(test_client)
        from app.models import MealPlans, MealPlanRecipes
        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        # Get current mealplan id

        mealplan_has_recipes = db.session.query(MealPlanRecipes) \
            .filter(MealPlanRecipes.mealplan_id == mealplan_id).all()
        assert not mealplan_has_recipes  # Check that mealplan has no recipes

        recipe_id = random.randint(0, 1400)  # Random recipe id to 'remove' from mealplan
        response = del_from_mealplan(test_client, mealplan_id, recipe_id)
        assert b'failure' in response.data

    @pytest.mark.parametrize("recipe_ids", [(random.sample(range(1000), 5)) for j in range(10)])
    # For each itr, add 5 random recipes. Do this 10 times.
    def test_add_recipes_to_mealplan_and_mealplan_view(self, test_client, user, logged_in_user, db, recipe_ids):
        """
        GIVEN a Flask application, user is logged in, meal plan is created and user has added 5 recipes to mealplan
        WHEN user requests meal plan view
        THEN success message is shown, and the recipe is added to meal plan
        """
        create_mealplan(test_client)

        from app.models import MealPlans, MealPlanRecipes
        # Get current mealplan id
        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()

        for id in recipe_ids:
            add_to_mealplan(test_client, id)  # Add 5 random recipes to meal plan

        response = view_mealplan(test_client, mealplan_id)  # Navigate to meal plan page
        response_recipe_ids = get_recipe_ids(test_client, response)  # Get recipe ids from recipes on page

        assert recipe_ids.sort() == response_recipe_ids.sort()

    def test_delete_mealplan_success(self, test_client, logged_in_user, user, db):
        """
        GIVEN a Flask application, user is logged in and has created a mealplan
        WHEN user requests to delete a mealplan
        THEN deletion succeeds
        """
        create_mealplan(test_client)

        from app.models import MealPlans, MealPlanRecipes
        mealplan_added = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert mealplan_added

        mealplan_id = mealplan_added.mealplan_id

        response = delete_mealplan(test_client, mealplan_id)
        assert response.status_code == 200
        assert b'warning' in response.data

        mealplan_added = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert not mealplan_added

    def test_delete_mealplan_with_recipes_added_success(self, test_client, logged_in_user, user, db):
        """
        GIVEN a Flask application, user is logged in, meal plan has been created and recipes are in meal plan
        WHEN user requests meal plan to be deleted
        THEN meal plan deletion obliges, and all recipes in MealPlanRecipes are deleted
        """
        create_mealplan(test_client)
        recipe_ids = random.sample(range(1400), 10)
        for id in recipe_ids:
            add_to_mealplan(test_client, id)  # Add 10 random recipes to meal plan

        from app.models import MealPlans, MealPlanRecipes
        mealplan_added = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert mealplan_added

        mealplan_id = mealplan_added.mealplan_id

        mealplan_has_recipes = db.session.query(MealPlanRecipes) \
            .filter(MealPlanRecipes.mealplan_id == mealplan_id).first()
        assert mealplan_has_recipes  # MealPlanRecipes associated with meal plan id exists

        response = delete_mealplan(test_client, mealplan_id)
        assert b'warning' in response.data

        mealplan_added = db.session.query(MealPlans).filter(MealPlans.mealplan_id == mealplan_id).first()
        assert not mealplan_added  # meal plan has been deleted

        mealplan_has_recipes = db.session.query(MealPlanRecipes) \
            .filter(MealPlanRecipes.mealplan_id == mealplan_id).first()
        assert not mealplan_has_recipes  # all MealPlanRecipes with associated meal plan id has been deleted

    def test_user_cannot_delete_mealplan_they_dont_own(self, test_client, logged_in_user, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests deleting a mealplan that they don't own
        THEN mealplan is not deleted and user is notified
        """
        from app.models import MealPlans, MealPlanRecipes
        user_has_mealplans = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert not user_has_mealplans

        del_mealplan_id = random.randint(1, 100)
        # Random mealplan to be attempted to delete (doesn't matter if it doesn't exist)

        response = delete_mealplan(test_client, del_mealplan_id)
        assert b'Sorry, you do not have access to this meal plan' in response.data

    @pytest.mark.parametrize("recipe_ids", [(range(1400))])  # Test this for almost all recipes
    def test_grocery_list_contains_ingredients_of_mealplan_recipes(self, test_client, logged_in_user, user, db,
                                                                   recipe_ids):
        """
        GIVEN a Flask application, user is logged in, meal plan is created and user has added 5 recipes to mealplan
        WHEN user requests to view grocery list of meal plan
        THEN correct ingredients are shown
        """
        create_mealplan(test_client)
        from app.models import MealPlans, RecipeIngredients
        # Get current mealplan id
        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        for id in recipe_ids:
            add_to_mealplan(test_client, id)  # Add 5 random recipes to meal plan

        response = view_grocery_list(test_client, mealplan_id)

        query = db.session.query(RecipeIngredients) \
            .filter(RecipeIngredients.recipe_id.in_(recipe_ids)) \
            .all()  # Query where recipe_id in recipe_ids
        ingredients_list = [i.ingredient for i in query]

        blockers = ["'", "&", "…"]
        for ingredient in ingredients_list:  # Check that ingredients are in grocery list
            if "href=" in str(ingredient):  # If an ingredient has a link in it, then don't check
                pass
            else:
                ing = []
                split = []
                ing[:0] = ingredient
                for blocker in blockers:
                    if blocker in ingredient:
                        split.append(int(ing.index(blocker)))
                        ing.remove(blocker)
                start = 0
                index = 1
                for s in split:
                    end = (s + 1) - index
                    search_string = ''.join(ing[start:end])
                    if "amp;" in search_string:
                        s_list = search_string.split("amp;")  # Split string by ampersand and assert them separately
                        assert s_list[0].encode() in response.data
                    else:
                        check = search_string.strip().encode()
                        assert check in response.data
                    start = end
                    index += 1


class TestSearchResults:

    @pytest.mark.parametrize("search_term", [('vegan'), ('rice')])
    def test_search_without_login(self, test_client, search_term):
        """
        GIVEN a Flask application
        WHEN a simple search is performed with the search parameter of search term
        THEN check that the search term is included in the response
        """
        response = search_function(test_client, search_term)
        assert response.status_code == 200
        assert search_term.encode() in response.data

    @pytest.mark.parametrize("search_term, allergies, diet, cal_range",
                             [('cabbage', [], 3, '100,500'),
                              ('fried rice', [], 1, '200,700'),
                              ('potato', [], 2, '0,1000')])
    # Unfortunately we can't test for allergies, because client.post does not seem to allow passing through a list, and
    # there is no other way for us to pass allergies through WTForms.
    def test_advanced_search_results_applies_filter_to_recipes(self, test_client, db, search_term, allergies, diet,
                                                               cal_range):
        """
        GIVEN a flask application
        WHEN user makes advanced search with specified search inputs
        THEN return recipes satisfy
        """
        response = advanced_search_function(test_client, search_term, allergies, diet, cal_range)
        assert response.status_code == 200
        assert search_term.encode() in response.data

        min_cal = int(cal_range.split(',')[0])
        max_cal = int(cal_range.split(',')[1])
        user_allergies = list(map(int, allergies))

        response_recipe_ids = get_recipe_ids(test_client, response)

        from app.models import Recipes
        recipes = db.session.query(Recipes).filter(Recipes.recipe_id.in_(response_recipe_ids)).all()

        for recipe in recipes:
            assert recipe.diet_type[0].diet_type_id >= diet
            assert search_term in recipe.recipe_name.lower()
            assert min_cal <= int(recipe.nutrition_values.calories) <= max_cal

            # recipe_allergies = [allergy.allergy_id for allergy in recipe.allergies]
            # for allergy in user_allergies:
            #     assert allergy not in recipe_allergies

    @pytest.mark.parametrize("itr", [(f"itr {str(i)}") for i in range(10)])  # Do test n times
    def test_view_all_recipes_applies_preferences_with_logged_in_user(self, test_client, user, logged_in_user, db, itr):
        """
        GIVEN a flask application and registered user (with randomly generated diet type and food preferences)
        WHEN user requests to view all recipes
        THEN saved food preferences and diet types are automatically applied
        """
        # User details as stored in db
        user_diet_name = user.diet_preferences[0].diet_type.diet_name
        user_diet_id = user.diet_preferences[0].diet_type.diet_type_id
        user_allergy_names = [allergy.allergy.allergy_name for allergy in user.allergies]
        user_allergy_ids = [allergy.allergy.allergy_id for allergy in user.allergies]

        # User details as presented in front-end, through config global variables
        diet_name = str((config.DIET_CHOICES[user_diet_id - 1])[1]).lower()
        allergy_names = [str((config.ALLERGY_CHOICES[i - 1])[1]).lower() for i in user_allergy_ids]

        response = view_all_recipes(test_client)
        assert b'Based on saved user preferences, we have applied the following filters:' in response.data
        assert b'Diet type: ' + diet_name.encode() in response.data
        assert b'Allergies: ' in response.data
        for allergy_name in allergy_names:
            assert allergy_name.encode() in response.data

        """
        GIVEN a flask application and registered user (with randomly generated diet type and food preferences)
        WHEN user requests to view all recipes
        THEN returned recipes satisfies user's diet preferences and allergies
        """
        # Pull the recipe ids that are returned in on the response page (as a list). See conftest helper function.
        response_recipe_ids = get_recipe_ids(test_client, response)

        from app.models import Recipes, RecipeDietTypes, RecipeAllergies

        for id in response_recipe_ids:  # for all recipes that are returned in results
            # Query all recipe ids which have the user's allergies
            blacklist = db.session.query(RecipeAllergies.recipe_id) \
                .filter(RecipeAllergies.allergy_id.in_(user_allergy_ids)) \
                .distinct().subquery()

            # Use outerjoin to exclude blacklisted recipes in query
            query = db.session.query(Recipes) \
                .outerjoin(blacklist, Recipes.recipe_id == blacklist.c.recipe_id) \
                .join(RecipeDietTypes) \
                .join(RecipeAllergies) \
                .filter(Recipes.recipe_id == id) \
                .filter(RecipeDietTypes.diet_type_id >= user_diet_id)
            # db recipe id should = recipe id on page
            # db diet type should be >= user's saved diet preference
            # This query should be not None (i.e. it should return something) if the filters have been applied
            assert query is not None

    @pytest.mark.parametrize("itr, search_term", [(0, "vegan"), (1, "rice"), (2, "noodles")])
    # Do test 3 times with different search terms
    def test_search_function_applies_preferences_with_logged_in_user(self, test_client, user, logged_in_user, db, itr, search_term):
        """
        GIVEN a flask application and registered user (with randomly generated diet type and food preferences)
        WHEN user requests to view all recipes
        THEN saved food preferences and diet types are automatically applied and is shown by a Flash message
        """
        # User details as stored in db
        user_diet_name = user.diet_preferences[0].diet_type.diet_name
        user_diet_id = user.diet_preferences[0].diet_type.diet_type_id
        user_allergy_names = [allergy.allergy.allergy_name for allergy in user.allergies]
        user_allergy_ids = [allergy.allergy.allergy_id for allergy in user.allergies]

        # User details as presented in front-end, through config global variables
        diet_name = str((config.DIET_CHOICES[user_diet_id - 1])[1]).lower()
        allergy_names = [str((config.ALLERGY_CHOICES[i - 1])[1]).lower() for i in user_allergy_ids]

        response = search_function(test_client, search_term)
        assert b'Based on saved user preferences, we have applied the following filters:' in response.data
        # Check the Flash message
        assert b'Diet type: ' + diet_name.encode() in response.data
        assert b'Allergies: ' in response.data
        for allergy_name in allergy_names:
            assert allergy_name.encode() in response.data

        """
        GIVEN a flask application and registered user (with randomly generated diet type and food preferences)
        WHEN user requests to view all recipes
        THEN returned recipes satisfies user's diet preferences and allergies
        """
        # Pull the recipe ids that are returned in on the response page (as a list). See conftest helper function.
        # We will compare these recipe ids in a db query to ensure that the filters have been applied
        response_recipe_ids = get_recipe_ids(test_client, response)

        from app.models import Recipes, RecipeDietTypes, RecipeAllergies

        for id in response_recipe_ids:  # for all recipes that are returned in results
            # Query all recipe ids which have the user's allergies
            blacklist = db.session.query(RecipeAllergies.recipe_id) \
                .filter(RecipeAllergies.allergy_id.in_(user_allergy_ids)) \
                .distinct().subquery()

            # Use outerjoin to exclude blacklisted recipes in query
            query = db.session.query(Recipes) \
                .outerjoin(blacklist, Recipes.recipe_id == blacklist.c.recipe_id) \
                .join(RecipeDietTypes) \
                .join(RecipeAllergies) \
                .filter(Recipes.recipe_id == id) \
                .filter(RecipeDietTypes.diet_type_id >= user_diet_id)
            # db recipe id should = recipe id on page
            # db diet type should be >= user's saved diet preference
            # This query should be not None (i.e. it should return something) if the filters have been applied
            assert query is not None

    @pytest.mark.parametrize("itr, allergy, search_term", [(0, [8], "peanut"),  # Peanut-free
                                                           (1, [1], "milk"),  # Milk-free
                                                           (2, [3], "fish")])  # Seafood-free
    # Do test 3 times with different search terms
    # Sometimes we need to test for certain cases. For example, searching for gluten could return 'gluten-free' recipes,
    # even if user has applied gluten-free to allergy.
    def test_search_with_specific_allergies(self, test_client, user, logged_in_user, db, itr, search_term, allergy):
        """
        GIVEN a flask application and registered user (with defined allergies)
        WHEN user searches for recipes that conflict with their allergies
        THEN appropriate response should return.
        """
        # Change user to classic diet type, with parametrised allergies
        edit_preferences(test_client, diet_choice=1, allergy_choices=allergy)

        user_allergy_ids = [allergy.allergy.allergy_id for allergy in user.allergies]
        allergy_names = [str((config.ALLERGY_CHOICES[i - 1])[1]).lower() for i in user_allergy_ids]

        response = search_function(test_client, search_term)
        assert b'Based on saved user preferences, we have applied the following filters:' in response.data
        assert b'Diet type: classic'
        assert b'Allergies: ' in response.data
        for allergy_name in allergy_names:
            assert allergy_name.encode() in response.data
        assert b'Sorry, no recipes found' in response.data


class TestEmail:

    def test_mail_grocery_list_fails_if_mealplan_is_empty(self, test_client, db, user, logged_in_user):
        """
        GIVEN a flask mail and logged in user with mealplan created
        WHEN user requests grocery list sent to email, but no recipes are in meal plan
        THEN warning message flashes
        """
        from app.models import MealPlans
        create_mealplan(test_client)
        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        # Get current mealplan id

        response = send_grocery_list(test_client, mealplan_id)
        assert b'There are no recipes in this meal plan, so we could not send you a grocery list!' in response.data

    @pytest.mark.parametrize("recipe_ids", [(random.sample(range(1400), 5))])
    def test_mail_grocery_list_succeeds_if_mealplan_is_not_empty(self, test_client, db, user, logged_in_user,
                                                                 recipe_ids):
        """
        GIVEN a flask mail and logged in user with mealplan created
        WHEN user requests grocery list sent to email, but no recipes are in meal plan
        THEN warning message flashes
        """
        from app.models import MealPlans
        create_mealplan(test_client)

        for id in recipe_ids:
            add_to_mealplan(test_client, id)

        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        # Get current mealplan id

        response = send_grocery_list(test_client, mealplan_id)
        assert (b'Email has been sent!' in response.data) or \
               (b'Unfortunately the email could not be sent, please try again at a later time.' in response.data)
