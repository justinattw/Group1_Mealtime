from flask import render_template, Blueprint, request, flash, redirect, url_for, session, make_response
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from markupsafe import escape
from sqlalchemy import outerjoin
from sqlalchemy.exc import IntegrityError

from app import db
from app.main.forms import AdvSearchRecipes
from app.models import Users, Recipes, RecipeIngredients, RecipeInstructions, NutritionValues, RecipeAllergies, \
    Allergies, UserDietPreferences, UserAllergies, DietTypes
from app.main.search_functions import search_function


bp_errors = Blueprint('errors', __name__)

@bp_errors.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/csrf_error.html', reason=e.description), 400