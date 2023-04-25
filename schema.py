from marshmallow import Schema, fields, ValidationError, validate

from constants import BASIC_PLAN, PREMIUM_PLAN


class BaseSchema(Schema):
  pass


class UserUpdateSchema(BaseSchema):
  first_name = fields.String(required=False,
                             error_messages={
                               'required': 'this field is mandatory',
                               'invalid': 'invalid, pass a string'
                             })
  last_name = fields.String(required=False,
                            error_messages={
                              'required': 'this field is mandatory',
                              'invalid': 'invalid, pass a string'
                            })
  dob = fields.Date(required=False,
                    error_messages={
                      'required': 'this field is mandatory',
                      'invalid': 'invalid, pass a date in yyyy-mm-dd format'
                    })
  country = fields.String(required=False,
                          validate=validate.Length(min=2, max=2,
                                                   error='use the Alpha-2 country code, e.g. NG'),
                          error_messages={
                            'invalid': 'use the Alpha-2 country code, e.g. NG'
                          })
  timezone = fields.String(required=False,
                           error_messages={
                             'invalid': 'invalid timezone'
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


class CreateSubscriptionSchema(BaseSchema):
  plan = fields.String(required=True,
                       validate=validate.OneOf([BASIC_PLAN, PREMIUM_PLAN]),
                       error_messages={
                         'required': 'this field is mandatory.',
                         'invalid': 'invalid, pass a valid string.'
                       })
  Authorization = fields.String(required=True,
                                error_messages={
                                  'required': 'this field is mandatory.',
                                  'invalid': 'invalid, pass a valid string.'
                                })

  payment_provider = fields.String(required=False,
                                   validate=validate.OneOf(['paystack', 'stripe']),
                                   error_messages={
                                      'invalid': 'invalid, pass either paystack or stripe.'
                                })

class AddApplicationSchema(BaseSchema):
  app = fields.String(required=True,
                      error_messages={
                        'required': 'this field is mandatory.',
                        'invalid': 'invalid, pass a valid string.'
                      })
  Authorization = fields.String(required=True,
                                error_messages={
                                  'required': 'this field is mandatory.',
                                  'invalid': 'invalid, pass a valid string.'
                                })


def validate_request(json_object, schema: BaseSchema):
  try:
    return True, schema.load(json_object)
  except ValidationError as error:
    return False, error.messages
