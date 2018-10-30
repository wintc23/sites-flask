from .. import db
from flask import request, current_app, jsonify
from . import api
from .decorators import permission_required
from functools import reduce
from ..models import Post

@api.route('/posts/', methods=["GET", "POST"])
def get_posts():
  page = request.args.get('page', 1, type = int)
  pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
    page, per_page = current_app.config['FLASK_POSTS_PER_PAGE'],
    error_out = False)
  posts = pagination.items
  post_json_list = reduce(lambda x, y: x.append(y.abstract_json()) or x, posts, [])
  return jsonify({
    "list": post_json_list,
    "pages": pagination.pages,
    "page": page
  })

@api.route('/post/', methods=["GET"])
def get_post():
  post_id = request.args.get('id')
  post = Post.query.get_or_404()
  return jsonify(post.to_json())