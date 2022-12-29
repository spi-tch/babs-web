from util.app import db


class Application(db.Model):
  __tablename__ = 'applications'
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  user_uuid = db.Column(db.String, nullable=False)
	