from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import outerjoin
from sqlalchemy.exc import IntegrityError

from app import db
from app.main.forms import AdvSearchRecipes, CalorieSearch
from app.models import Users, Recipes, RecipeIngredients, RecipeInstructions, NutritionValues, RecipeAllergies, \
    Allergies, RecipeDietTypes, UserDietPreferences, UserAllergies
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
    return render_template('index.html', name=name)


@bp_main.route('/recipes/<id_num>', methods=['GET'])
def view_recipe(id_num):
    recipe = db.session.query(Recipes).filter(Recipes.recipe_id == id_num).one()
    allergies = db.session.query(Allergies, RecipeAllergies)\
                    .join(RecipeAllergies)\
                    .filter(RecipeAllergies.recipe_id == id_num)\
                    .all()
    ingredients = db.session.query(RecipeIngredients)\
                    .filter(RecipeIngredients.recipe_id == id_num)\
                    .all()
    steps = db.session.query(RecipeInstructions)\
                .filter(RecipeInstructions.recipe_id == id_num)\
                .all()
    nutrition = db.session.query(NutritionValues)\
                    .filter(NutritionValues.recipe_id == id_num)\
                    .one()
    return render_template("view_recipe.html", recipe=recipe, ingredients=ingredients, steps=steps, nutrition=nutrition, allergies=allergies)


@bp_main.route('/recipes', methods=['GET'])
def recipes():
    recipes = search_function()
    # return render_template("recipes.html", recipes=recipes)
    return render_template("search_results.html", results=recipes)

@bp_main.route('/search', methods=['POST', 'GET'])
def search():
    # If user is logged in, then search with user preference values
    # If user is not logged in, then search with no additional parameters

    if request.method == 'POST':
        term = request.form['search_term']

        try:
            user_id = current_user.id
        except:
            user_id = None

        if user_id is not None:
            diet_type, = db.session.query(UserDietPreferences.diet_type_id).filter_by(user_id=user_id).first()
            allergies = db.session.query(UserAllergies.allergy_id).filter_by(user_id=user_id).all()
            print("Diet type: ", diet_type)
            print("Allergies: ", allergies)

            celery, gluten, seafood, eggs, lupin, mustard, tree_nuts, peanuts, sesame, soybeans, dairy = False, False, False, False, False, False, False, False, False, False, False
        else:
            diet_type=1
            celery, gluten, seafood, eggs, lupin, mustard, tree_nuts, peanuts, sesame, soybeans, dairy = False, False, False, False, False, False, False, False, False, False, False

        results = search_function(search_term=term,
                                  diet_type=diet_type,
                                  celery_free=celery,
                                  gluten_free=gluten,
                                  seafood_free=seafood,
                                  eggs_free=eggs,
                                  lupin_free=lupin,
                                  mustard_free=mustard,
                                  tree_nuts_free=tree_nuts,
                                  peanuts_free=peanuts,
                                  sesame_free=sesame,
                                  soybeans_free=soybeans,
                                  dairy_free=dairy)

        if not results:
            flash("No recipes found.")
            return redirect('/')

        return render_template('search_results.html', results=results)

    else:
        return redirect(url_for('main.index'))


@bp_main.route('/advanced_search', methods=['POST', 'GET'])
def advanced_search():
    form = AdvSearchRecipes()

    if request.method == 'POST' and form.validate():

        search_term = form.search_term.data

        diet_types_dict = {"classic": 1,
                           "pescatarian": 2,
                           "vegetarian": 3,
                           "vegan": 4}
        diet_type = diet_types_dict[form.diet_type.data]

        results = search_function(search_term=search_term,
                                  diet_type=diet_type,
                                  celery_free=form.celery.data,
                                  gluten_free=form.gluten.data,
                                  seafood_free=form.seafood.data,
                                  eggs_free=form.eggs.data,
                                  lupin_free=form.lupin.data,
                                  mustard_free=form.mustard.data,
                                  tree_nuts_free=form.tree_nuts.data,
                                  peanuts_free=form.peanuts.data,
                                  sesame_free=form.sesame.data,
                                  soybeans_free=form.soybeans.data,
                                  dairy_free=form.dairy.data)

        return render_template('search_results.html', results=results)

    return render_template('advanced_search.html', form=form)


@bp_main.route('/delete_cookie')
def delete_cookie():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('name', '', expires=datetime.now())
    return response

# A public user profile viewer
# @bp_main.route('/user/<userid>')
# def show_user(userid):
#     user = Users.query.filter_by(id=userid).first_or_404(description='There is no user {}'.format(userid))
#     return render_template('account.html', user=user)


@bp_main.route('/meal_planner', methods=['POST', 'GET'])
def meal_planner():
    form = CalorieSearch()

    if request.method == 'POST':
        upper = form.upper_callimit.data
        lower = form.lower_callimit.data

        results = db.session.query(NutritionValues) \
            .filter(NutritionValues.calories <= upper) \
            .filter(NutritionValues.calories >= lower) \
            .all()

        # return render_template('search_results.html', results=results)

    return render_template('meal_planner.html', form=form)