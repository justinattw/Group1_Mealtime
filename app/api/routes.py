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
from flask_login import login_user
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


@bp_api.errorhandler(401)
def not_authorised():
    error = {
        'status': 401,
        'message': 'You must provide username and password to access this resource',
    }
    response = jsonify(error)
    return make_response(response, 404)


@http_auth.verify_password
def verify_password(email, password):
    user = Users.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return False
    return True


@bp_api.route('/recipes', methods=['GET'])
# @http_auth.login_required
def read_recipes():
    recipes = Recipes.query.all()
    json = jsonify(recipes=[r.serialize for r in recipes])
    return make_response(json, 200)


@bp_api.route('/recipes/<int:recipe_id>', methods=['GET'])
@http_auth.login_required
def read_recipe(recipe_id):
    recipe = Recipes.query.filter_by(recipe_id=recipe_id).first_or_404()
    json = jsonify(recipe=recipe.serialize)
    return make_response(json, 200)


@bp_api.route('/users', methods=['POST'])
def create_user():
    username = request.args.get('username')
    password = request.args.get('password')
    if username is None or password is None:
        json = jsonify({'message': 'Missing username or password'})
        return make_response(json, 400)
    if Users.query.filter_by(name=username).first() is not None:
        json = jsonify({'message': 'Duplicate username'})
        return make_response(json, 400)
    user = Users(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    json = jsonify({'user_id': '{}'.format(user.id), 'name': '{}'.format(user.name)})
    return make_response(json, 201)


# @bp_api.route('/users', method=['POST'])
# def login_user():
#     email = request.args.get('email')
#     password = request.args.get('password')
#     if email is None or password is None:
#         json = jsonify({'message': 'Missing email and/or password'})
#         return make_response(json, 400)
#
#     user = Users.query.filter_by(email=email).first()
#     if user is None:
#         json = jsonify({'message': 'No account is associated with this email'})
#         return make_response(json, 400)
#     if not user.check_password(password):
#         json = jsonify({'message': 'Incorrect password'})
#         return make_response(json, 400)
#     login_user(user)  # log the user in
#     json = jsonify({'user_id': f'{user.id}',
#                     'email': f'{user.email}',
#                     'first_name': f'{user.first_name}',
#                     'last_name': f'{user.last_name}'
#                     })
#     return make_response(json, 201)

