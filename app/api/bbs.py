from ..models import BBS
from flask import request, jsonify, current_app

@api.route('/user_bbs/', methods=['POST'])
def get_bbs_by_user():

  author_id = request.json.get('author_id'):
  bbs = map(lambda x:x.to_json(), BBS.query.filter_by(author_id=author_id).all())
  data = {
    'bbs': list(bbs)
  }
  return jsonify(data)

@api.route('/bbs/', methods=['POST'])
def get_bbs():
  page = request.json.get('page', 1)
  per_page = current_app.config['FLASK_BBS_PER_PAGE']
  pagination = BBS.query.filter(BBS.response_id.equal(None)).order_by(BBS.timestamp.desc()).paginate(page,per_page=per_page,error_out=False)
  pages = pagination.pages
  bbs = map(lambda x:x.to_json, pagination.items)
  return jsonify({
    'bbs': list(bbs),
    'pages': pages,
    'page': page
  })

