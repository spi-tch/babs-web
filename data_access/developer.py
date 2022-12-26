import enum

from util.app import db


class ParamType(enum.Enum):
  path = "path"
  body = "body"
  query = "query"


class Developer(db.Model):
  __tablename__ = 'developer'
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String, nullable=False, unique=True, index=True)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  email = db.Column(db.String(50), nullable=True, index=True)
  country = db.Column(db.String(2), nullable=True)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)

  def __repr__(self):
    return f'Developer: {self.first_name} {self.last_name}; Country: {self.country}'


class API(db.Model):
  __tablename__ = 'api'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  name = db.Column(db.String, nullable=False, unique=True, index=True)
  description = db.Column(db.String, nullable=False)
  developer_id = db.Column(db.Integer, db.ForeignKey('developer.id'), nullable=False)


class Request(db.Model):
  __tablename__ = 'request'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  api_id = db.Column(db.String, nullable=False)
  action_id = db.Column(db.String, nullable=False)
  developer_id = db.Column(db.String, nullable=False)
  method = db.Column(db.String, nullable=False)
  request_body = db.Column(db.Boolean, nullable=False)
  url = db.Column(db.String, nullable=False)
  auth_type = db.Column(db.String, nullable=False)
  intent = db.Column(db.String, nullable=False, unique=True, index=True)
  description = db.Column(db.String, nullable=True)
  example = db.Column(db.String, nullable=True)
  slots_example = db.Column(db.String, nullable=True)


class Response(db.Model):
  __tablename__ = 'response'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
  response_code = db.Column(db.Integer, nullable=False)
  response_body = db.Column(db.String, nullable=False)
  response_type = db.Column(db.String, nullable=False)
  data_object = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=True)


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
  request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
  entity_type = db.Column(db.String, nullable=True)
  value_type = db.Column(db.String, nullable=True)
