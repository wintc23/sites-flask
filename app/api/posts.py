from .. import db
from flask import request, current_app, jsonify
from . import api
from .decorators import permission_required
from functools import reduce
from ..models import Post, PostType, Tag
from .errors import bad_request
from .decorators import login_required

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
  post = Post.query.get_or_404(post_id)
  return jsonify(post.to_json())

@api.route('/post-types/', methods=["GET"])
def get_types():
  types = PostType.query.all()
  lstTypeJson = reduce(lambda x, y: x.append(y.to_json()) or x, types, [])
  return jsonify({
    "list": lstTypeJson
  })

@api.route('/type-manage/', methods=["POST"])
@login_required()
def manage_type():
  type_list = request.json.get('list')
  if type_list:
    for post_type in type_list:
      type_id = post_type.get('id')
      type_name = post_type.get('name')
      type_alias = post_type.get('alias')
      if not type_name or not type_alias:
        continue
      if type_id:
        old_type = PostType.query.get(type_id) 
        if (old_type):
          old_type.name = type_name
          old_type.alias = type_alias
          db.session.add(old_type)
      else:
        new_type = PostType(name = type_name, alias = type_alias)
        db.session.add(new_type)
    return jsonify({ "message": '请求成功' })
  return bad_request('参数错误')  

# @api.route('/type-set/', methods=["POST"])
# @login_required()
# def set_type():
#   type_id = request.json.get('id')
#   post_type = PostType.query.get_or_404(type_id)
#   post_name = request.json.get('name')
#   if post_name:
#     post_type.name = post_name
#     db.session.add(post_type)
#     return jsonify({ 'message': '请求成功' })
#   return bad_request('请求参数错误！')

# @api.route('/type-add/', methods=["POST"])
# def add_type():
#   post_name = request.json.get('name')
#   if post_name:
#     if not PostType.query.filter(name = post_name):
#       postType = PostType(name = post_name)
#       db.session.add(postType)
#       db.session.commit()
#       return jsonify({ 'message': '添加成功' })
#     else:
#       return bad_request('该文章类型已存在', True)
#   return bad_request('参数错误')

@api.route('/post-tags/', methods=["GET"])
def get_tags():
  tags = Tag.query.all()
  lstTag = reduce(lambda x, y : x.append(y.to_json()) or x, tags, [])
  return jsonify({
    "list": lstTag
  })

@api.route('/tag-manage/', methods=["POST"])
@login_required()
def manage_tag():
  tag_list = request.json.get('list')
  if tag_list:
    for tag in tag_list:
      tag_id = tag.get('id')
      tag_name = tag.get('name')
      tag_alias = tag.get('alias')
      if not tag_alias or not tag_name:
        return
      if tag_id:
        old_tag = Tag.query.get(tag_id) 
        if (old_tag):
          old_tag.name = tag_name
          old_tag.alias = tag_alias
          db.session.add(old_tag)
      else:
        new_tag = Tag(name = tag_name, alias = tag_alias)
        db.session.add(new_tag)
    return jsonify({ "message": '请求成功' })
  return bad_request('参数错误')

# @api.route('/tag-set/', methods=["POST"])
# @login_required()
# def set_tag():
#   tag_id = request.json.get('id')
#   tag = Tag.query.get_or_404(tag_id)
#   tag_name = request.json.get('name')
#   if tag_name:
#     tag.name = tag_name
#     db.session.add(tag)
#     return jsonify({ 'message': '请求成功' })

# @api.route('/tag-add/', methods = ["POST"])
# @login_required()
# def add_tag():
#   tag_name = request.json.get('name')
#   if tag_name:
#     if not Tag.query.filter(name = tag_name):
#       tag = Tag(name=tag_name)
#       db.session.add(tag)
#       db.session.commit()
#       return jsonify({ 'message': '添加成功' })
#     else:
#       return bad_request('该标签已存在', True)
#   return bad_request('参数错误')
