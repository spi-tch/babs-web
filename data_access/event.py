from util.app import db


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String, nullable=False, index=True)
    type_name = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.TIMESTAMP)
    intent_name = db.Column(db.String, nullable=True)
    action_name = db.Column(db.String, nullable=True)
    data = db.Column(db.JSON, nullable=True)
