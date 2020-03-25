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
    Allergies, UserDietPreferences, UserAllergies, DietTypes
from app.main.search_functions import search_function

from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFError
from markupsafe import escape
import sqlalchemy
from sqlalchemy import outerjoin
from sqlalchemy.exc import IntegrityError

bp_main = Blueprint('main', __name__)


@bp_main.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/csrf_error.html', reason=e.description), 400


@bp_main.route('/')
def index(name=""):
    # Demonstration of use of a session cookie. Display email as the name if the session cookie is there.
    if 'name' in request.cookies:
        name = request.cookies.get('name')
    if 'name' in session:
        name = escape(session['name'])

    return render_template('main/index.html', name=name, body_id="hero_image")


@bp_main.route('/recipes/<id_num>', methods=['GET'])
def view_recipe(id_num):
    recipe = db.session.query(Recipes).filter(Recipes.recipe_id == id_num).one()

    allergies = db.session.query(Allergies, RecipeAllergies) \
        .join(RecipeAllergies) \
        .filter(RecipeAllergies.recipe_id == id_num) \
        .all()
    ingredients = db.session.query(RecipeIngredients) \
        .filter(RecipeIngredients.recipe_id == id_num) \
        .all()
    steps = db.session.query(RecipeInstructions) \
        .filter(RecipeInstructions.recipe_id == id_num) \
        .all()
    nutrition = db.session.query(NutritionValues) \
        .filter(NutritionValues.recipe_id == id_num) \
        .one()
    return render_template("main/view_recipe.html", recipe=recipe, ingredients=ingredients, steps=steps,
                           nutrition=nutrition, allergies=allergies)


@bp_main.route('/recipes', methods=['GET'])
def recipes():
    query = search_function()
    page = request.args.get('page', 1, type=int)
    recipes = query.paginate(page, 20, False)

    next_url = url_for('main.recipes', page=recipes.next_num) if recipes.has_next else None
    prev_url = url_for('main.recipes', page=recipes.prev_num) if recipes.has_prev else None

    # return render_template("recipes.html", recipes=recipes)
    return render_template("main/search_results.html", results=recipes.items, next_url=next_url,
                           prev_url=prev_url)


@bp_main.route('/search', methods=['POST', 'GET'])
def search():
    # If user is logged in, then search with user preference values
    # If user is not logged in, then search with no additional parameters

    if request.method == 'POST':
        term = request.form['search_term']

        if current_user.is_authenticated:

            user_id = current_user.id
            diet_type, = db.session.query(UserDietPreferences.diet_type_id).filter_by(user_id=user_id).first()
            # Query for allergies based on user_id, then turn query to list
            allergy_query = db.session.query(UserAllergies.allergy_id).filter_by(user_id=user_id).all()
            allergy_list = [value for value, in allergy_query]

            query = search_function(search_term=term, diet_type=diet_type, allergy_list=allergy_list)
            page = request.args.get('page', 1, type=int)
            recipes = query.paginate(page, 20, False)


        else:
            query = search_function(search_term=term)
            page = request.args.get('page', 1, type=int)
            recipes = query.paginate(page, 20, False)

        if not recipes:
            flash("No recipes found.")
            return redirect('/')

        next_url = url_for('main.recipes', page=recipes.next_num) if recipes.has_next else None
        prev_url = url_for('main.recipes', page=recipes.prev_num) if recipes.has_prev else None

        return redirect(url_for('main.recipes', results=recipes.items, next_url=next_url,
                               prev_url=prev_url))

        # return render_template('main/search_results.html', results=recipes.items, next_url=next_url,
        #                        prev_url=prev_url)

    else:
        return redirect(url_for('main.index'))


@bp_main.route('/advanced_search', methods=['POST', 'GET'])
def advanced_search():
    form = AdvSearchRecipes()

    if request.method == 'POST':
        range = form.hidden.data.split(',')
        search_term = form.search_term.data

        allergy_list = list(map(int, form.allergies.data))
        diet_type = int(form.diet_type.data)

        results = search_function(search_term=search_term,
                                  diet_type=diet_type,
                                  min_cal=float(range[0]),
                                  max_cal=float(range[1]),
                                  allergy_list=allergy_list)

        page = request.args.get('page', 1, type=int)
        recipes = results.paginate(page, 20, False)

        next_url = url_for('main.advanced_search', page=recipes.next_num) if recipes.has_next else None
        prev_url = url_for('main.advanced_search', page=recipes.prev_num) if recipes.has_prev else None

        return render_template('main/search_results.html', results=recipes.items, next_url=next_url,
                               prev_url=prev_url)

    return render_template('main/advanced_search.html', form=form)


# A public user profile viewer
@bp_main.route('/favourites')
@login_required
def favourites():
    user = Users.query.filter_by(id=current_user.id) \
        .first_or_404(description='There is no user {}'.format(current_user.id))
    return render_template('auth/favourites.html', user=user)


@bp_main.route('/delete_cookie')
def delete_cookie():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('name', '', expires=datetime.now())
    return response


@bp_main.route('/meal_planner', methods=['POST', 'GET'])
def meal_planner():
    if request.method == 'POST':
        None

    return render_template('main/meal_planner.html')
