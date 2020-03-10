from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import outerjoin
from sqlalchemy.exc import IntegrityError

from app import db
from app.main.forms import AdvSearchRecipes
from app.models import Users, Recipes, RecipeIngredients, RecipeInstructions, NutritionValues, RecipeAllergies, \
    Allergies, RecipeDietTypes

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

        # Uncomment out below if users must have a search term to look up recipes
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

    if request.method == 'POST' and form.validate():

        search_term = form.search_term.data

        diet_types_dict = {"classic": 1,
                           "pescatarian": 2,
                           "vegetarian": 3,
                           "vegan": 4}
        diet_type = diet_types_dict[form.diet_type.data]  # return diet_type id with key:value pair

        allergies = []
        if form.celery.data:
            allergies.append(1)
        if form.gluten.data:
            allergies.append(2)
        if form.seafood.data:
            allergies.append(3)
        if form.eggs.data:
            allergies.append(4)
        if form.lupin.data:
            allergies.append(5)
        if form.mustard.data:
            allergies.append(6)
        if form.tree_nuts.data:
            allergies.append(7)
        if form.peanuts.data:
            allergies.append(8)
        if form.sesame.data:
            allergies.append(9)
        if form.soybeans.data:
            allergies.append(10)
        if form.dairy.data:
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

        return render_template('search_results.html', results=results)

    return render_template('advanced_search.html', form=form)


@bp_main.route('/delete_cookie')
def delete_cookie():
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('name', '', expires=datetime.now())
    return response


@bp_main.route('/user/<userid>')
def show_user(userid):
    user = Users.query.filter_by(id=userid).first_or_404(description='There is no user {}'.format(userid))
    return render_template('show_user.html', user=user)


# Mealplans route, query for mealplans based on logged in user_id,
# @bp_main.route('/mealplans')
# def mealplans(name):
