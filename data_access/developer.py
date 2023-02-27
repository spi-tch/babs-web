import enum

from util.app import db


class ParamType(enum.Enum):
  path = "path"
  body = "body"
  query = "query"


# class Developer(db.Model):
#   __tablename__ = 'developer'
#   id = db.Column(db.Integer, primary_key=True)
#   uuid = db.Column(db.String, nullable=False, unique=True, index=True)
#   first_name = db.Column(db.String(30), nullable=False)
#   last_name = db.Column(db.String(30), nullable=True)
#   created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
#   updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
#                          onupdate=db.func.current_timestamp())
#   email = db.Column(db.String(50), nullable=True, index=True)
#   country = db.Column(db.String(2), nullable=True)
#   is_admin = db.Column(db.Boolean, nullable=False, default=False)
#
#   def __repr__(self):
#     return f'Developer: {self.first_name} {self.last_name}; Country: {self.country}'


# class API(db.Model):
#   __tablename__ = 'api'
#   id = db.Column(db.Integer, primary_key=True)
#   created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
#   updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
#                          onupdate=db.func.current_timestamp())
#   name = db.Column(db.String, nullable=False, unique=True, index=True)
#   description = db.Column(db.String, nullable=False)
#   developer_id = db.Column(db.Integer, db.ForeignKey('developer.id'), nullable=False)


class Request(db.Model):
  __tablename__ = 'request'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  api_id = db.Column(db.String, nullable=False)
  uuid = db.Column(db.String, nullable=False)
  developer_id = db.Column(db.String, nullable=False)
  method = db.Column(db.String, nullable=False)
  request_body = db.Column(db.Boolean, nullable=False)
  url = db.Column(db.String, nullable=False)
  auth_type = db.Column(db.String, nullable=False)
  intent = db.Column(db.String, nullable=False, unique=True, index=True)
  description = db.Column(db.String, nullable=True)
  example = db.Column(db.String, nullable=True)
  slot_sample = db.Column(db.String, nullable=True)
  app_name = db.Column(db.String, nullable=True)


class Response(db.Model):
  __tablename__ = 'response'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
  response_code = db.Column(db.Integer, nullable=False)
  sample = db.Column(db.String, nullable=True)
  structure = db.Column(db.String, nullable=True)


class Parameter(db.Model):
  __tablename__ = 'parameter'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  name = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  type = db.Column(db.Enum(ParamType), nullable=False)
  default_value = db.Column(db.String, nullable=True)
  mandatory = db.Column(db.Boolean, nullable=False, default=True)
  request = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
  entity_type = db.Column(db.String, nullable=True)
  value_type = db.Column(db.String, nullable=True)


class Intent(db.Model):
  __tablename__ = 'intents'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  name = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  requests = db.Column(db.String, nullable=True)
  intent_type = db.Column(db.String, nullable=False)
  threshold = db.Column(db.Float, nullable=True)
  transfer = db.Column(db.String, nullable=True)


class Watch(db.Model):
  __tablename__ = 'watch'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  user_id = db.Column(db.String, db.ForeignKey('user.uuid'), nullable=False)
  latest = db.Column(db.String, nullable=False)
  app_name = db.Column(db.String, nullable=False)


def delete_watch(user_id, app_name):
  watch = Watch.query.filter_by(user_id=user_id, app_name=app_name).first()
  if watch:
    db.session.delete(watch)
    db.session.commit()
    return True
  return False


def create_watch(user_id, app_name, latest):
  watch = Watch(user_id=user_id, app_name=app_name, latest=latest)
  db.session.add(watch)
  db.session.commit()
  return True
