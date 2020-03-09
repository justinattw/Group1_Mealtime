from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import and_, or_, outerjoin
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import with_polymorphic, load_only

from app import db
from app.main.forms import AdvSearchRecipes
# from app.models import Course, Student, Teacher, User
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

    if form.diet_type.data == "classic":
        diet_type = 1
    elif form.diet_type.data == "pescatarian":
        diet_type = 2
    elif form.diet_type.data == "vegetarian":
        diet_type = 3
    else:
        diet_type = 4

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

    if request.method == 'POST' and form.validate():
        # results = db.session.query(Recipes) \
        #     .join(RecipeDietTypes, Recipes.recipe_id == RecipeDietTypes.recipe_id) \
        #     .join(RecipeAllergies, Recipes.recipe_id == RecipeAllergies.recipe_id) \
        #     .filter(RecipeDietTypes.diet_type_id >= diet_type) \
        #     .filter(~Recipes.recipe_id.in_(blacklist)) \
        #     .filter(Recipes.recipe_name.contains(search_term)).all()

        # blacklist recipes if user does not want certain recipes
        blacklist = db.session.query(RecipeAllergies.recipe_id) \
            .filter(RecipeAllergies.allergy_id.in_(allergies)).distinct().subquery()

        # blacklist_list = [value for value, in blacklist] # return recipe_id
        # print(len(blacklist_list))

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


@bp_main.route('/user/<name>')
def show_user(name):
    user = Users.query.filter_by(first_name=name).first_or_404(description='There is no user {}'.format(name))
    return render_template('show_user.html', user=user)

# Mealplans route, query for mealplans based on logged in user_id,
# @bp_main.route('/mealplans')
# def mealplans(name):
