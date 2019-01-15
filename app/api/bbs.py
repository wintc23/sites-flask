from ..models import BBS
from flask import request, jsonify, current_app, g
from sqlalchemy import or_
from .decorators import login_required
from .errors import bad_request
from . import api
from .. import db

@api.route('/user_bbs/', methods=['POST'])
def get_bbs_by_user():
  author_id = request.json.get('author_id')
  bbs = map(lambda x:x.to_json(), BBS.query.filter_by(author_id=author_id).all())
  data = {
    'bbs': list(bbs)
  }
  return jsonify(data)

@api.route('/bbs/', methods=['POST'])
def get_bbs():
  page = request.json.get('page', 1)
  per_page = current_app.config['FLASK_BBS_PER_PAGE']
  pagination = BBS.query.filter(BBS.response_id == None).order_by(BBS.timestamp.desc()).paginate(page,per_page=per_page,error_out=False)
  total = pagination.total
  id_list = list(map(lambda x:x.id, pagination.items))
  bbs_list = pagination.items
  if len(id_list):
    filter_list = list(map(lambda x: BBS.root_id == x, id_list))
    bbs_list.extend(BBS.query.filter(or_(*filter_list)).all())
  bbs_list = list(map(lambda x:x.to_json(), bbs_list))
  return jsonify({
    'bbs': bbs_list,
    'total': total,
    'page': page
  })

@api.route('/add_bbs/', methods=["POST"])
@login_required()
def add_bbs():
  content = request.json.get('content', '')
  if not content:
    return bad_request('留言内容不能为空', True)
  params = {
    'body': content,
    'author_id': g.current_user.id,
  }
  response_id = request.json.get('responseId')
  if response_id:
    reponse = BBS.query.get_or_404(response_id)
    params['response_id'] = response_id
    params['root_id'] = reponse.root_id if reponse.root_id else reponse.id
  else:
    params['root_id'] = 0
  bbs = BBS(**params)
  try:
    db.session.add(bbs)
    db.session.commit()
    return jsonify({ 'message': '保存成功' })
  except:
    db.session.rollback()
  return bad_request('服务器处理请求报错', True)


