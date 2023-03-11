import logging
import os
import uuid

from flask import Blueprint, request, redirect
from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token

import services
from data_access import find_user_by_uuid
from schema import CreateSubscriptionSchema, validate_request

subscription = Blueprint('subscription', __name__)

logger = logging.getLogger(__name__)
billing_service = services.BillingService()


@subscription.route(f'/subscription', methods=['POST'])
def create_subscription():
  """Create a new subscription, use Stripe"""
  request_data = request.form
  valid, data = validate_request(request_data, CreateSubscriptionSchema())

  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    auth = request_data['Authorization'].split(' ')[1]
    claims = verify_oauth2_token(auth, requests.Request(),
                                 audience=os.getenv('GOOGLE_CLIENT_ID'))
  except Exception as e:
    logger.error(e)
    message = {"success": False, "message": "Bad request"}
    return message, 400

  try:
    if not claims['email_verified']:
      raise Exception('User email has not been verified by Google.')
    __id__ = uuid.uuid5(uuid.NAMESPACE_URL, claims['email'])
    user = find_user_by_uuid(str(__id__))
    status, message, session = billing_service.create_checkout_session(data, user)
    if status:
      return redirect(session.url, code=303)

    if "update" in message.lower() and "requested" in message.lower():
      message = {'success': True, 'message': message}
      return message, 200
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to create subscription.'}
    return message, 500


@subscription.route(f'/billing_portal', methods=['POST'])
def create_portal():
  try:
    request_data = request.form
    auth = request_data['Authorization'].split(' ')[1]
    claims = verify_oauth2_token(auth, requests.Request(),
                                 audience=os.getenv('GOOGLE_CLIENT_ID'))
  except Exception as e:
    logger.error(e)
    message = {"success": False, "message": "Bad request"}
    return message, 400

  try:
    if not claims['email_verified']:
      raise Exception('User email has not been verified by Google.')
    __id__ = uuid.uuid5(uuid.NAMESPACE_URL, claims['email'])
    user = find_user_by_uuid(str(__id__))
    status, message, session = billing_service.create_portal_session(user)
    if status:
      return redirect(session.url, code=303)
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to create portal session.'}
    return message, 500


@subscription.route(f'/webhooks/stripe', methods=['POST'])
def stripe_webhook():
  """Handle Stripe webhooks"""
  try:
    status, message, _ = billing_service.handle_stripe_webhook(
      request.get_data(as_text=True),
      request.headers.get('Stripe-Signature')
    )
    if status:
      return {'success': True}, 200
    return {'success': False, 'message': message}, 400
  except Exception as e:
    logger.error(e)
    return {'success': False, 'message': 'Unable to handle webhook'}, 400


@subscription.route(f'/payment', methods=['GET'])
def get_payment_status():
  """Get payment status"""
  try:
    status, message, data = billing_service.get_payment_status(request.environ["user"].id)
    if status:
      return {'success': True, 'data': data}, 200
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to get payment status.'}
    return message, 500
