import logging
import os
from datetime import datetime

from stripe.api_resources.invoice import Invoice
from stripe.api_resources.subscription import Subscription

from constants import PREMIUM_PLAN, BASIC_PLAN
from data_access import get_stripe_customer, find_user_by_id, update_user
from exceptns import UserNotFoundException

logger = logging.getLogger(__name__)


class UserNotFoundError:
  pass


# def handle_successful_payment(invoice: Invoice):
#   customer = invoice["customer"]
#   customer = get_stripe_customer(customer)
#   if customer is not None:
#     if user := find_user_by_id(customer.user_id):
#       ts = datetime.utcfromtimestamp(invoice["lines"]["data"][0]["period"]["end"])
#       # update_user(user, {"sub_expires_at": ts})
#       logger.warning(f"Timestamp of period end: {ts}")
#
#   logger.info("Payment succeeded")


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
  # technically, we don't need to do anything here because the subscription is already deleted
  # but we can send a mail to the user to let them know that their subscription has been cancelled
  # we will use mailgun for that.
  pass
  customer = subscription["customer"]
  customer = get_stripe_customer(customer)
  if customer is not None:
    # if user := find_user_by_id(customer.user_id):
    #   update_user(user, {"tier": BASIC_PLAN, "sub_expires_at": None})
    pass
  logger.info("Subscription deleted")
