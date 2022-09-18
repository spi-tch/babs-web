from util.app import db


class AuthService:
  def __init__(self):
    self.auth_query = db.session.query(Auth)
