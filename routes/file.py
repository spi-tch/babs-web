from flask import send_file, Blueprint

file = Blueprint('file', __name__)


@file.route('/logo', methods=['GET'])
def logo():
  return send_file('static/images/logo.png')


@file.route('/logowtext', methods=['GET'])
def logowtext():
  return send_file('static/images/logowtext.png')
