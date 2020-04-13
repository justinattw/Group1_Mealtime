#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test/test_main.py:

Pytests tests for main views and methods (relating to files in app/main/)

Parameterised testing: https://blog.testproject.io/2019/07/16/python-test-automation-project-using-pytest/
"""
__authors__ = "Danny Wallis, Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Danny Wallis", "Justin Wong"]
__status__ = "Development"

import config
from test.conftest import search_function, add_to_favourites, view_recipe, view_favourites, view_about, \
    view_mealplanner, login_test_user, del_from_mealplan, view_grocery_list, view_mealplan, get_recipe_ids, \
    view_advanced_search, advanced_search_function, create_mealplan, view_all_recipes, add_to_mealplan, delete_mealplan

import pytest
import random
from sqlalchemy.orm.exc import ObjectDeletedError
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
        THEN response is invalid
        """
        response = view_favourites(test_client)
        assert b'You must be logged in to view that page.' in response.data  # Method not allowed


    def test_view_favourites_valid_with_login(self, test_client, user):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests to view their favourites (before having added a favourite recipe)
        THEN response is always valid and correct data is displayed
        """
        login_test_user(test_client)
        response = view_favourites(test_client)
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
        THEN view is successful
        """
        response = view_all_recipes(test_client)
        assert response.status_code == 200


    def test_view_advanced_search(self, test_client):
        """
        GIVEN a Flask application
        WHEN the 'view_advanced_search' page is requested'
        THEN response is valid
        """
        response = view_advanced_search(test_client)
        assert response.status_code == 200


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

    def test_add_to_favourite(self, test_client, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites
        THEN check response is valid
        """
        login_test_user(test_client)

        from app.models import UserFavouriteRecipes, Recipes

        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
        # indicating how many recipes there are.
        # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
        # can upload + delete their uploaded recipes, this will need to be changed.

        rand_favourite = random.randint(1, number_of_recipes)  # generate a random favourite recipe_id to test
        response = add_to_favourites(test_client, rand_favourite)  # add random favourite recipe to favourites
        assert response.status_code == 200

        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites
        THEN check the recipe has been added to the database in the correct model/ tabe
        """
        fav_query = db.session.query(UserFavouriteRecipes) \
            .filter(UserFavouriteRecipes.user_id == user.id) \
            .filter(UserFavouriteRecipes.recipe_id == rand_favourite) \
            .first()
        assert fav_query is not None

        """
        GIVEN a Flask application and user is logged in
        WHEN user adds a (random) recipe to favourites that has already been added
        THEN check that an IntegrityError/ ObjectDeletedError occurs from SQLAlchemy
        """
        with pytest.raises(ObjectDeletedError):
            # Although in the routes we expect IntegrityError, ObjectDeletedError is raised in test environment because of
            # the way the dbs interact
            response = add_to_favourites(test_client, rand_favourite)


    def test_add_to_favourites_and_view_favourites(self, test_client, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user favourites a new recipe and views their Favourites page
        THEN response is valid (response code is 200), and favourited recipe_name is in the response data
        """
        login_test_user(test_client)

        from app.models import Recipes

        number_of_recipes, = db.session.query(func.max(Recipes.recipe_id)).first()  # Query the highest recipe_id,
        # indicating how many recipes there are.
        # This query assumes that there are no empty recipe_ids up to the highest id. If we ever add a feature where users
        # can upload + delete their uploaded recipes, this will need to be changed.

        favourite = random.randint(1, number_of_recipes)
        response = add_to_favourites(test_client, favourite)
        assert response.status_code == 200

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
        response = view_mealplanner(test_client)
        assert response.status_code == 200
        assert b'You must be logged in' in response.data


    def test_view_mealplanner_with_login(self, test_client, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN the 'view_mealplanner' page is requested'
        THEN response is valid
        """
        login_test_user(test_client)
        response = view_mealplanner(test_client)
        assert response.status_code == 200
        assert b'Meal Planner' in response.data
        assert b"You don't have any meal plans" in response.data


    @pytest.mark.parametrize("random_mealplan", [(random.randint(0, 1000)) for i in range(5)])  # random mealplan 5 times
    def test_cannot_view_others_mealplan(self, test_client, user, random_mealplan):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests to view mealplan that they do not own
        THEN error message flashes
        """
        login_test_user(test_client)

        # User has no mealplans, so they cannot view any. We can feed any mealplan_id into the url and it should fail
        url = '/view_mealplan/' + str(random_mealplan)

        response = test_client.get(url, follow_redirects=True)
        assert b'Sorry, you do not have access to this meal plan' in response.data


    def test_create_new_mealplan_success(self, test_client, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN the 'create_mealplan' is requested
        THEN response is valid and meal plan is added to database, and that you can view the meal plan
        """
        login_test_user(test_client)

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


    def test_cannot_add_new_mealplan_while_old_mealplan_is_empty(self, test_client, user, db):
        """
        GIVEN a Flask application and user is logged in
        WHEN user requests 'create_mealplan' twice (thus on the second request, the active meal plan is empty)
        THEN appropriate error messages flashes on second attempt
        """
        login_test_user(test_client)
        create_mealplan(test_client) # Create meal plan once
        response = create_mealplan(test_client) # Create meal plan twice
        assert b'Your most recent meal plan' in response.data
        assert b'has no recipes. Please make use of it before' in response.data
        assert b'creating a new meal plan' in response.data
        assert response.status_code == 200


    def test_delete_mealplan_success(self, test_client, user, db):
        """
        GIVEN a Flask application, user is logged in and has created a mealplan
        WHEN user requests to delete a mealplan
        THEN deletion succeeds
        """
        login_test_user(test_client)
        create_mealplan(test_client)

        from app.models import MealPlans, MealPlanRecipes
        mealplan_added = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        mealplan_id = mealplan_added.mealplan_id
        assert mealplan_added

        response = delete_mealplan(test_client, mealplan_id)
        assert response.status_code == 200
        assert b'warning' in response.data

        mealplan_added = db.session.query(MealPlans).filter(MealPlans.user_id == user.id).first()
        assert not mealplan_added



    def test_add_and_delete_recipe_from_mealplan(self, test_client, user, db):
        """
        GIVEN a Flask application, user is logged in and meal plan is created
        WHEN user adds new recipe to mealplan
        THEN success message is shown, and the recipe is added to meal plan
        """
        login_test_user(test_client)
        create_mealplan(test_client)

        from app.models import MealPlans, MealPlanRecipes
        mealplan_id, = db.session.query(MealPlans.mealplan_id).filter(MealPlans.user_id == user.id).first()
        # Get current mealplan id

        recipe_id = random.randint(0, 1000)
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


    @pytest.mark.parametrize("search_term, allergies, diet, hidden",
                             [('cabbage', ['1', '4'], 3, '100,500'),
                              ('fried rice', ['3', '8', '9'], 1, '200,700'),
                              ('potato', ['5'], 2, '0,1000')])
    def test_advanced_search_results_correct(self, test_client, search_term, allergies, diet, hidden):

        response = advanced_search_function(test_client, search_term, allergies, diet, hidden)
        assert response.status_code == 200
        assert search_term.encode() in response.data


    @pytest.mark.parametrize("itr", [(i) for i in range(10)])  # Do test n times
    def test_view_all_recipes_applies_preferences_with_logged_in_user(self, test_client, user, db, itr):
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

        login_test_user(test_client)
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




