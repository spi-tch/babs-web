import logging
import os

from flask import Blueprint, request

import services
from schema import CreateSubscriptionSchema, validate_request

VERSION = f"v{os.getenv('BABS_APP_VERSION')}"
subscription = Blueprint('subscription', __name__)

logger = logging.getLogger(__name__)
billing_service = services.BillingService()


@subscription.route(f'/{VERSION}/subscription', methods=['POST'])
def create_subscription():
  """Create a new subscription, use Stripe"""
  request_data = request.json
  valid, data = validate_request(request_data, CreateSubscriptionSchema())

  if not valid:
    message = {'errors': data, 'success': False}
    return message, 400

  try:
    status, message, session = billing_service.create_checkout_session(data, request.environ["user"])
    if status:
        # todo: fix redirect issue
      return {"redirect_url": session.url}, 200

    if "update" in message.lower() and "requested" in message.lower():
      message = {'success': True, 'message': message}
      return message, 200
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to create subscription.'}
    return message, 500


@subscription.route(f'/{VERSION}/billing_portal', methods=['POST'])
def create_portal():
  try:
    status, message, session = billing_service.create_portal_session(request.environ["user"].id)
    if status:
        # todo: fix redirect issue
      return {"redirect_url": session.url}, 200
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to create portal session.'}
    return message, 500


@subscription.route(f'/{VERSION}/cards', methods=['GET'])
def get_cards():
  try:
    status, message, cards = billing_service.get_cards(request.environ["user"].id)
    if status:
      return {'success': True, 'cards': cards}
    message = {'success': False, 'message': message}
    return message, 400
  except Exception as e:
    logger.error(e)
    message = {'success': False, 'message': f'Unable to get cards.'}
    return message, 500


@subscription.route(f'/webhooks/stripe', methods=['POST'])
def stripe_webhook():
  """Handle Stripe webhooks"""
  try:
    billing_service.handle_stripe_webhook(
      request.data,
      request.headers.get('Stripe-Signature')
    )
    return {'success': True}, 200
  except Exception as e:
    logger.error(e)
    return {'success': False, 'message': 'Unable to handle webhook'}, 400


@subscription.route(f'/{VERSION}/payment', methods=['GET'])
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
