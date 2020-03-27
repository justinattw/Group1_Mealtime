#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/main/routes.py:

This document includes WTForms for authentication methods.
Authentication methods include signup, login, edit account details and log out.
"""
__authors__ = "Ethan Low, Danny Wallis, and Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Ethan Low", "Danny Wallis", "Justin Wong"]
__status__ = "Development"

from app import db
from app.main.forms import AdvSearchRecipes
from app.models import Users, Recipes, RecipeIngredients, RecipeInstructions, NutritionValues, RecipeAllergies, \
    Allergies, UserDietPreferences, UserAllergies, UserFavouriteRecipes, MealPlanRecipes, MealPlans
from app.main.search_functions import search_function
import config

from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from markupsafe import escape

bp_main = Blueprint('main', __name__)


@bp_main.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/csrf_error.html', reason=e.description), 400


@bp_main.route('/')
def index(name=""):
    """
    The home (index) page

    :param name: finds user's name if logged in
    :return: the index html page with a background
    """
    # Demonstration of use of a session cookie. Display email as the name if the session cookie is there.
    if 'name' in request.cookies:
        name = request.cookies.get('name')
    if 'name' in session:
        name = escape(session['name'])

    return render_template('main/index.html', name=name, body_id="hero_image")


@bp_main.route('/recipe/<recipe_id>', methods=['GET'])
def view_recipe(recipe_id):
    recipe = db.session.query(Recipes).filter(Recipes.recipe_id == recipe_id).one()

    allergies = db.session.query(Allergies, RecipeAllergies) \
        .join(RecipeAllergies) \
        .filter(RecipeAllergies.recipe_id == recipe_id) \
        .all()
    ingredients = db.session.query(RecipeIngredients) \
        .filter(RecipeIngredients.recipe_id == recipe_id) \
        .all()
    steps = db.session.query(RecipeInstructions) \
        .filter(RecipeInstructions.recipe_id == recipe_id) \
        .all()
    nutrition = db.session.query(NutritionValues) \
        .filter(NutritionValues.recipe_id == recipe_id) \
        .one()
    return render_template("main/view_recipe.html", recipe=recipe, ingredients=ingredients, steps=steps,
                           nutrition=nutrition, allergies=allergies)


@bp_main.route('/recipes', methods=['GET'])
def recipes():
    """
    This route takes

    :return:
    """

    # This dictionary allows search parameters to be kept in the page, so that they are saved even when navigating to
    # next/ prev urls
    args_dict = {'search_term': request.args.get('search_term', ""),
                 'allergy_list': request.args.get('allergy_list', [], type=list),
                 'diet_type': request.args.get('diet_type', 1, type=int),
                 'min_cal': request.args.get('min_cal', 0, type=int),
                 'max_cal': request.args.get('max_cal', 1000, type=int),
                 'max_time': request.args.get('max_time', 99999, type=int)}

    # The following code related to pagination is adapted from:
    #
    # Title: The Flask Mega-Tutorial Part IX: Pagination
    # Author: Miguel Grinberg
    # Date: 2018
    # Availability: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ix-pagination
    # [Accessed 25 March 2020]

    query = search_function(**args_dict)
    page = request.args.get('page', 1, type=int)  # Get current page of results
    recipes = query.paginate(page, config.RECIPES_PER_PAGE, False)

    next_url = url_for('main.recipes', **args_dict, page=recipes.next_num) if recipes.has_next else None
    prev_url = url_for('main.recipes', **args_dict, page=recipes.prev_num) if recipes.has_prev else None

    # return render_template("recipes.html", recipes=recipes)
    return render_template("main/search_results.html",
                           results=recipes.items,
                           **args_dict,
                           next_url=next_url, prev_url=prev_url)


@bp_main.route('/view_all_recipes', methods=['GET'])
def view_all_recipes():
    """
    Redirect route to view all recipes

    :return: the recipes route, with no search parameters (so that it queries all recipes)
    """
    return redirect(url_for('main.recipes'))


@bp_main.route('/search', methods=['POST', 'GET'])
def search():
    """
    Route for the simple search bar, which only takes in one search_term to match recipe names.

    If user is logged in (is_authenticated), then the search function will apply the user's saved diet preferences and
    allergies in the search.
    If user is not logged in, then search progresses with only the search_term.

    :return: the recipes route, passing appropriate search parameters
    """
    if request.method == 'POST':
        search_term = request.form['search_term']

        if current_user.is_authenticated:

            user_id = current_user.id
            diet_type, = db.session.query(UserDietPreferences.diet_type_id).filter_by(user_id=user_id).first()
            allergy_query = db.session.query(UserAllergies.allergy_id).filter_by(user_id=user_id).all()
            allergy_list = [value for value, in allergy_query]  # Turn allergies query results into a list

            return redirect(url_for('main.recipes', search_term=search_term, diet_type=diet_type, allergy_list=allergy_list))

        else:
            return redirect(url_for('main.recipes', search_term=search_term))

    else:
        return redirect(url_for('main.index'))


@bp_main.route('/advanced_search', methods=['POST', 'GET'])
def advanced_search():
    """
    Route for advanced search page, allowing user to fill in a form to query recipes based on entered parameters.

    :return: the recipes route with associated query
    """
    form = AdvSearchRecipes()

    if request.method == 'POST':
        range = form.hidden.data.split(',')

        args_dict = {'search_term': form.search_term.data,
                     'allergy_list': list(map(int, form.allergies.data)),
                     'diet_type': int(form.diet_type.data),
                     'min_cal': float(range[0]),
                     'max_cal': float(range[1])
                     }

        return redirect(url_for('main.recipes', **args_dict))

    return render_template('main/advanced_search.html', form=form)


@bp_main.route('/add_to_mealplan/<recipe_id>', methods=['GET', 'POST'])
@login_required
def add_to_mealplan(recipe_id):
    """
    Allows user to add recipe to the most recent mealplan

    :param recipe_id: adds recipe associated with recipe_id to mealplan
    :return: stays on same page
    """

    # Get the most recent mealplan by taking max(mealplan_id). We will add recipe to this mealplan.
    mealplan_id, = db.session.query(func.max(MealPlans.mealplan_id)) \
        .filter(MealPlans.user_id == current_user.id).first()

    print(mealplan_id)

    if mealplan_id is None:
        flash("Please create a meal plan first!")
    else:
        try:
            db.session.add(MealPlanRecipes(mealplan_id=mealplan_id, recipe_id=recipe_id))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("This recipe is already in your mealplan!")

    print(f"Added recipe {recipe_id} to mealplan {mealplan_id}")
    return '', 204


@bp_main.route('/add_to_favourites/<recipe_id>', methods=['GET', 'POST'])
@login_required
def add_to_favourites(recipe_id):
    """
    Allows user to add recipe to favourites. Duplicate favourites are handled with IntegrityError (based on UNIQUE
    constraint in SQLite database)

    :param recipe_id: adds recipe associated with recipe_id to favourites of user with associated user_id
    :return: stays on same page
    """
    try:
        db.session.add(UserFavouriteRecipes(user_id=current_user.id, recipe_id=recipe_id))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("This recipe is already in your favourites!")
    print(f"Added recipe {recipe_id} to user {current_user.id}'s favourites")
    return '', 204


@bp_main.route('/favourites')
@login_required
def favourites():
    """
    Views user's favourite recipes.

    :return: favourites html page with corresponding favourite recipes.
    """
    user = Users.query.filter_by(id=current_user.id).first_or_404(
        description='There is no user {}'.format(current_user.id))

    query = db.session.query(Recipes) \
        .join(UserFavouriteRecipes, Recipes.recipe_id == UserFavouriteRecipes.recipe_id) \
        .filter(UserFavouriteRecipes.user_id == current_user.id)

    page = request.args.get('page', 1, type=int)  # Get current page of results
    recipes = query.paginate(page, config.RECIPES_PER_PAGE, False)

    next_url = url_for('main.favourites', page=recipes.next_num) if recipes.has_next else None
    prev_url = url_for('main.favourites', page=recipes.prev_num) if recipes.has_prev else None

    return render_template('main/favourites.html', user=user, results=recipes.items, next_url=next_url,
                           prev_url=prev_url)


@bp_main.route('/mealplanner', methods=['POST', 'GET'])
def mealplanner():
    if request.method == 'POST':
        None

    return render_template('main/mealplanner.html')


@bp_main.route('/about', methods=['POST', 'GET'])
def about():
    """
    A page describing the Mealtime project, its aims, licenses, and contributors.

    :return: the 'About' html page
    """
    return render_template('main/about.html')


@bp_main.route('/delete_cookie')
def delete_cookie():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('name', '', expires=datetime.now())
    return response
