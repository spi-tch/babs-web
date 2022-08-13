from flask import Blueprint, render_template

home = Blueprint('home', __name__)


@home.route('/', methods=['GET', 'POST'])
def _home():
  render_template('index.html')
