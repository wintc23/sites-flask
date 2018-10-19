from .. import db
from . import api
from .decorators import permission_required

@api.route('/posts/')
def get_posts():
  page = require.args.get('page', 1, type = int)
  # pagination = Post