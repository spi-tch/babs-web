from util.app import db


class BabsEvent(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False, index=True)
    type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), index=True)
    channel = db.Column(db.String, nullable=True)
    data = db.Column(db.JSON)
