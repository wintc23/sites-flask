from only import *
from flask import Flask

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def ping():
  return res_json('Hello world')

if __name__ == '__main__':
  app.run()