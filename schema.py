from marshmallow import Schema, fields, ValidationError, validate


class BaseSchema(Schema):
  pass


class UserUpdateSchema(BaseSchema):
  first_name = fields.String(required=True,
                             error_messages={
                               'required': 'this field is mandatory',
                               'invalid': 'invalid, pass a string'
                             })
  last_name = fields.String(required=True,
                            error_messages={
                              'required': 'this field is mandatory',
                              'invalid': 'invalid, pass a string'
                            })
  dob = fields.Date(required=True,
                    error_messages={
                      'required': 'this field is mandatory',
                      'invalid': 'invalid, pass a date in yyyy-mm-dd format'
                    })
  country = fields.String(required=True,
                          validate=validate.Length(min=2, max=2,
                                                   error='use the Alpha-2 country code, e.g. NG'),
                          error_messages={
                            'required': 'this field is mandatory',
                            'invalid': 'use the Alpha-2 country code, e.g. NG'
                          })


class UserRegistrationSchema(BaseSchema):
  token = fields.String(required=True,
                        error_messages={
                          'required': 'this field is mandatory. Send a valid JWT from Google.',
                        })


class UserVerificationSchema(BaseSchema):
  code = fields.Integer(required=True,
                        error_messages={
                          'required': 'this field is mandatory.',
                          'invalid': 'invalid, pass a 6-digit integer.'
                        })


class WaitlistSchema(BaseSchema):
  email = fields.Email(required=True,
                       error_messages={
                         'required': 'this field is mandatory.',
                         'invalid': 'invalid, use a valid email address'
                       })


class GetChannelSchema(BaseSchema):
  user_uuid = fields.String(required=True,
                            error_messages={
                              'required': 'this field is mandatory.',
                              'invalid': 'invalid, pass a valid string.'
                            })
  channel = fields.String(required=True,
                          error_messages={
                            'required': 'this field is mandatory.',
                            'invalid': 'channel must be valid.'
                          })


def validate_request(json_object, schema: BaseSchema):
  try:
    return True, schema.load(json_object)
  except ValidationError as error:
    return False, error.messages
