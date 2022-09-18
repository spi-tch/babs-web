from marshmallow import Schema, fields, ValidationError, validate


class BaseSchema(Schema):
  pass


class UserUpdateSchema(BaseSchema):
  phone_number = fields.String(required=True,
                               error_messages={
                                 'required': 'this field is mandatory',
                                 'invalid': 'invalid, pass a string'
                               })
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
  channel = fields.String(required=True,
                          validate=validate.OneOf(choices=['whatsapp', 'telegram'],
                                                  error='Supported channels are whatsapp & telegram.'),
                          error_messages={
                            'required': 'this field is mandatory',
                            'invalid': 'Supported channels are whatsapp & telegram.'
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


def validate_request(json_object, schema: BaseSchema):
  try:
    return True, schema.load(json_object)
  except ValidationError as error:
    return False, error.messages
