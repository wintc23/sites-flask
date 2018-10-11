from flask import Blueprint

api = Blueprint('auth', __name__)

from . import authentication, posts, users, comments, errors