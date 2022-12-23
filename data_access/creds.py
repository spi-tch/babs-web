
from util.app import db


class Creds(db.Model):
    __tablename__ = 'creds'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False, unique=True, index=True)
    value = db.Column(db.String, nullable=False)
