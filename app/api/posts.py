from .. import db
from flask import request, current_app, jsonify, g
from . import api
from .decorators import permission_required
from functools import reduce
from ..models import Post, PostType, Tag, Comment, Permission, Like
from .errors import bad_request, unauthorized
from .decorators import login_required

import sqlalchemy

@api.route('/posts/', methods=["POST"])
def get_posts():
  page = request.json.get('page', 1)
  post_type = request.json.get('type', 'blog')
  type_id = 0
  postType = PostType.query.filter_by(alias=post_type).first()
  pages = 0
  if postType:
    type_id = postType.id
    pagination = Post.query.filter_by(type_id=type_id).order_by(Post.timestamp.desc()).paginate(
      page, per_page = current_app.config['FLASK_POSTS_PER_PAGE'],
      error_out = False)
    posts = pagination.items
    post_json_list = reduce(lambda x, y: x.append(y.abstract_json()) or x, posts, [])
    pages = pagination.pages
  else:
    post_json_list = []
  return jsonify({
    "list": post_json_list,
    "pages": pages,
    "page": page
  })

@api.route('/post/', methods=["POST"])
def get_post():
  post_id = request.json.get('postId')
  addRead = request.json.get('addRead')
  type_id = 0
  post_type = request.json.get('postType')
  if post_type:
    postQuery = PostType.query.filter_by(alias=post_type)
    if postQuery.count() > 0:
      type_id = postQuery.first().id  
  post = Post.query.get_or_404(post_id)
  # if post.hide and post.author != g.current_user and (request.json.get('secretCode') != post.secretCode):
    # return bad_request('文章已被隐藏', True)
  if addRead:
    post.read_times += 1
    db.session.add(post)
  query = Post.query
  if type_id:
    query = query.filter_by(type_id = type_id)
  post_list = query.order_by(Post.timestamp.desc()).all()
  index = post_list.index(post)
  before = {}
  after = {}
  if index != -1:
    length = len(post_list)
    if (length > index + 1):
      post_before = post_list[index + 1]
      before = post_before.abstract_json()
    if (index - 1 >= 0):
      post_after = post_list[index - 1]
      after = post_after.abstract_json()
  json = post.to_json()
  json['before'] = before or None
  json['after'] = after or None
  if post.hide and post.author != g.current_user and (request.json.get('secretCode') != post.secretCode):
    json['body'] = ''
    json['body_html'] = ''
    json['error_secret'] = True
  return jsonify(json)

@api.route('/save-post/', methods=["POST"])
@login_required()
@permission_required(Permission.WRITE)
def save_post():
  post_id = request.json.get('id')
  if post_id:
    post = Post.query.get_or_404(post_id)
    if (post.author != g.current_user):
      return bad_request('非法请求')
    for tag in post.tags.all():
      if not tag.id in request.json['tags']:
        post.tags.remove(tag)
      else:
        request.json['tags'].remove(tag.id)
  else:
    post = Post(author = g.current_user)
  for tag_id in request.json['tags']:
    tag = Tag.query.get(tag_id)
    if tag:
      post.tags.append(tag)
  post.abstract_image = request.json['abstract_image']
  post.type = PostType.query.get(request.json['type'])
  post.title = request.json['title']
  post.body = request.json['body']
  post.body_html = request.json['body_html']
  post.abstract = request.json['abstract']
  post.hide = request.json['hide']
  post.secretCode = request.json['secretCode']
  db.session.add(post)
  try:
    db.session.commit()
  except:
    db.session.remove()
    response = jsonify({ 'error': 'database error', 'message': '数据出错，请重试' })
    return response
  return jsonify({'message': '保存成功', 'id': post.id })

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

@api.route('/add-comment/', methods=["POST"])
@login_required()
def add_comment():
  params = {}
  body = request.json.get('body', '')
  post_id = request.json.get('postId')
  response_id = request.json.get('responseId')
  if not body:
    return bad_request('评论不能为空', True)
  if not post_id:
    return bad_request('错误请求')
  params['body'] = body
  params['post_id'] = post_id
  params['author'] = g.current_user
  if response_id:
    response = Comment.query.get(response_id)
    if response:
      params['response'] = response
  comment = Comment(**params)
  db.session.add(comment)
  try:
    db.session.commit()
  except:
    db.session.rollback()
    return bad_request('数据库错误')
  return jsonify({ 'message': '评论成功' })

@api.route('/get-comments/', methods=["GET"])
def get_comments():
  post_id = request.args.get('postId')
  if not post_id:
    return bad_request('请求错误', True)
  post = Post.query.get(post_id)
  if not post:
    return bad_request('请求错误', True)
  return jsonify(post.comments_json())

# 返回最近的5篇文章
@api.route('/get-recent-posts/', methods=["GET"])
def get_recent_posts():
  pagination = Post.query.filter(Post.abstract_image != None).filter_by(hide=False).order_by(Post.timestamp.desc()).paginate(1, per_page=5)
  posts = pagination.items
  post_json_list = reduce(lambda x, y: x.append(y.abstract_json()) or x, posts, [])
  return jsonify({
    "list": post_json_list
  })

# 返回阅读数
@api.route('/get-hot-posts/', methods=["GET"])
def get_hot_posts():
  comment_sub = Comment.query.group_by(Comment.post_id).with_entities(Comment.post_id, sqlalchemy.func.count(Comment.post_id).label('count')).subquery()
  result = db.session.query(Post, comment_sub.c.count).join(comment_sub, Post.id == comment_sub.c.post_id).order_by(comment_sub.c.count.desc()).paginate(1, per_page=4)
  post_list = reduce(lambda x, y: x.append(y[0]) or x, result.items, [])

  like_sub = Like.query.group_by(Like.post_id).with_entities(Like.post_id, sqlalchemy.func.count(Like.post_id).label('count')).subquery()
  result = db.session.query(Post, like_sub.c.count).join(like_sub, Post.id == like_sub.c.post_id).order_by(like_sub.c.count.desc()).paginate(1, per_page=3)
  post_list.extend(reduce(lambda x, y: x.append(y[0]) or x, result.items, []))

  pagination = Post.query.filter_by(hide=False).order_by(Post.read_times.desc()).paginate(1, per_page=3)
  post_list.extend(pagination.items)

  post_list = reduce(lambda x, y: (x.append(y) if y not in x else x) or x, post_list, [])
  post_list = reduce(lambda x, y: x.append(y.abstract_json()) or x, post_list, [])
  return jsonify({
    "list": post_list
  })