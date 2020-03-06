from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_polymorphic

from app import db
from app.main.forms import AdvSearchRecipes
# from app.models import Course, Student, Teacher, User
from app.models import Users, Recipes, RecipeIngredients, RecipeInstructions, NutritionValues, RecipeAllergies, Allergies

bp_main = Blueprint('main', __name__)


@bp_main.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


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
    recipes = db.session.query(Recipes).all()
    return render_template("recipes.html", recipes=recipes)


@bp_main.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        term = request.form['search_term']
        # if term == "":
        #    flash("Enter a recipe to search for")
        #    return redirect('/')
        results = db.session.query(Recipes).filter(Recipes.recipe_name.contains(term)).all()
        if not results:
            flash("No recipes found.")
            return redirect('/')
        return render_template('search_results.html', results=results)
    else:
        return redirect(url_for('main.index'))


@bp_main.route('/advanced_search', methods=['POST', 'GET'])
def advanced_search():
    form = AdvSearchRecipes()
    search_term = form.search_term.data
    form.diet_type.data
    form.celery.data
    form.gluten.data
    seafood = BooleanField('Seafood-free')
    eggs = BooleanField('Eggs-free')
    lupin = BooleanField('Lupin-free')
    mustard = BooleanField('Mustard-free')
    tree_nuts = BooleanField('Tree nuts-free')
    peanuts = BooleanField('Peanuts-free')
    sesame = BooleanField('Sesame seeds-free')
    soybeans = BooleanField('Soybeans-free')

    if request.method == 'POST' and form.validate():


        results = Recipes.query.filter(Recipes.recipe_name.contains(search_term)).all()

        results = Recipes

        return render_template('search_results.html', results=results)

        db.users.filter(or_(db.users.name == 'Ryan', db.users.country == 'England'))

    return render_template('advanced_search.html', form=form)


@bp_main.route('/delete_cookie')
def delete_cookie():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('name', '', expires=datetime.now())
    return response


@bp_main.route('/user/<name>')
def show_user(name):
    user = Users.query.filter_by(first_name=name).first_or_404(description='There is no user {}'.format(name))
    return render_template('show_user.html', user=user)

# Mealplans route, query for mealplans based on logged in user_id,
# @bp_main.route('/mealplans')
# def mealplans(name):
