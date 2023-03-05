import logging
import os
from datetime import datetime

from stripe.api_resources.customer import Customer
from stripe.api_resources.payment_intent import PaymentIntent
from stripe.api_resources.subscription import Subscription

from constants import PREMIUM_PLAN, BASIC_PLAN
from data_access import get_stripe_customer, find_user_by_id, update_user, delete_stripe_customer
from data_access.payment import get_payment_for_user, create_payment
from exceptns import UserNotFoundException

logger = logging.getLogger(__name__)


class UserNotFoundError:
  pass


def handle_subscription_created_or_updated(subscription: Subscription):
  tier = subscription["items"]["data"][0]["price"]["id"]
  if tier == os.getenv("STRIPE_PREMIUM_PRICE_ID"):
    tier = PREMIUM_PLAN
  elif tier == os.getenv("STRIPE_BASIC_PRICE_ID"):
    tier = BASIC_PLAN
  customer = subscription["customer"]
  logger.info(f"Subscription created for customer {customer}")
  customer = get_stripe_customer(customer)
  if customer is None:
    raise UserNotFoundException("Stripe customer not found")
  if user := find_user_by_id(customer.user_id):
    expiry = datetime.utcfromtimestamp(subscription["current_period_end"])
    update_user(user, {"tier": tier, "sub_expires_at": expiry})
    pass
  logger.info("Subscription created")


def handle_subscription_deleted(subscription: Subscription):
  customer = subscription["customer"]
  customer = get_stripe_customer(customer)
  if customer is not None:
    if user := find_user_by_id(customer.user_id):
      update_user(user, {"tier": None, "sub_expires_at": None})
    pass
  logger.info("Subscription deleted")


def handle_payment_success_or_failure(payment_intent: PaymentIntent):
  customer = payment_intent["customer"]
  customer = get_stripe_customer(customer)
  if customer is None:
    raise UserNotFoundException("Stripe customer not found")
  user = find_user_by_id(customer.user_id)
  if user is None:
    raise UserNotFoundException("User not found")
  payment = get_payment_for_user(user.uuid)
  if payment is None:
    create_payment(user.uuid, payment_intent)
  else:
    update_user(user, {"tier": BASIC_PLAN, "sub_expires_at": None})


def handle_customer_deleted(customer: Customer):
  customer = delete_stripe_customer(customer["id"])
  if customer is not None:
    if user := find_user_by_id(customer.user_id):
      update_user(user, {"tier": None, "sub_expires_at": None})
    pass
  logger.info("Customer deleted")
