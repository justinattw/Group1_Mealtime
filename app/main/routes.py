from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import outerjoin
from sqlalchemy.exc import IntegrityError

from app import db
from app.main.forms import AdvSearchRecipes
from app.models import Users, Recipes, RecipeIngredients, RecipeInstructions, NutritionValues, RecipeAllergies, \
    Allergies, UserDietPreferences, UserAllergies, DietTypes
from app.main.search_functions import search_function

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
    recipes = search_function()
    # return render_template("recipes.html", recipes=recipes)
    return render_template("main/search_results.html", results=recipes)


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

            results = search_function(search_term=term, diet_type=diet_type, allergy_list=allergy_list)

        else:
            results = search_function(search_term=term)

        if not results:
            flash("No recipes found.")
            return redirect('/')

        return render_template('main/search_results.html', results=results)

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

        return render_template('main/search_results.html', results=results)

    return render_template('main/advanced_search.html', form=form)


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


# Mealplans route, query for mealplans based on logged in user_id,
# @bp_main.route('/mealplans')
# def mealplans(name):
