from flask import g, jsonify, request, current_app
from ..models import User, AnonymousUser
from .errors import bad_request, not_found
from . import api

@api.route('/userinfo/', methods=['GET'])
def get_user_info():
  user_id = request.args.get('id')
  user = User.query.get_or_404(user_id)
  if user:
    return jsonify(user.to_json())
  return bad_request('参数错误')

@api.route('/userid/', methods=["GET"])
def get_manager_id():
  user = User.query.filter_by(email=current_app.config['FLASK_ADMIN']).first()
  if user:
    return jsonify({ 'id': user.id })
  return not_found('无管理员信息', True)
