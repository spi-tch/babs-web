from typing import Text

from util.app import db


class GoogleCreds(db.Model):
  __tablename__ = "google_creds"
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String, nullable=False)
  refresh_token = db.Column(db.String, nullable=False)
  token_uri = db.Column(db.String, nullable=False)
  client_id = db.Column(db.String, nullable=False)
  client_secret = db.Column(db.String, nullable=False)
  scopes = db.Column(db.ARRAY(item_type=db.String), nullable=False)
  user = db.Column(db.String, nullable=False, index=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
