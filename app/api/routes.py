from flask import Blueprint, jsonify
from flask_login import login_required

from app import db

bp_api = Blueprint('api', __name__, url_prefix='/api')

