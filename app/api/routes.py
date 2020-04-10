#!usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app/api/routes.py:

This document includes routes concerning the Mealtime API.
The function of the API is to allow users to read (but not write) recipes, giving users easy access to our recipes.
"""
__authors__ = "Justin Wong"
__email__ = "justin.wong.17@ucl.ac.uk"
__credits__ = ["Justin Wong"]
__status__ = "Development"

from app import db
from app.models import Recipes, Users

from flask import Blueprint, jsonify, request, make_response
from flask_httpauth import HTTPBasicAuth

bp_api = Blueprint('api', __name__, url_prefix='/api')
http_auth = HTTPBasicAuth()


@bp_api.after_request
def add_header(response):
    # Apply same header to every response using @bp_api.after_request, as they all respond json
    # json response then we could apply the same header to every response using @bp_api.after_request
    response.headers['Content-Type'] = 'application/json'
    return response


@bp_api.errorhandler(404)
def not_found():
    error = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    response = jsonify(error)
    return make_response(response, 404)


@bp_api.route('/recipes', methods=['GET'])
def read_recipes():
    recipes = Recipes.query.all()
    json = jsonify(recipes=[r.serialize for r in recipes])
    return make_response(json, 200)


@bp_api.route('/recipes/<int:recipe_id>', methods=['GET'])
def read_recipe(recipe_id):
    recipe = Recipes.query.filter_by(recipe_id=recipe_id).first_or_404()
    json = jsonify(recipe=recipe.serialize)
    return make_response(json, 200)
