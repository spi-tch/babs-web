from util.app import db


class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String, nullable=False, unique=True, index=True)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  email = db.Column(db.String(50), nullable=True, index=True)
  dob = db.Column(db.DATE, nullable=True)
  country = db.Column(db.String(2), nullable=True)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  timezone = db.Column(db.String(30), nullable=True)

  def __repr__(self):
    return f'User: {self.first_name} {self.last_name}; Country: {self.country}'


class WaitList(db.Model):
  __tablename__ = 'wait_list'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  email = db.Column(db.String, nullable=False, index=True)
