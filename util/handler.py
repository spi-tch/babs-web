import logging
import os
import requests
from datetime import datetime

from stripe.api_resources.customer import Customer
from stripe.api_resources.payment_intent import PaymentIntent
from stripe.api_resources.subscription import Subscription

from constants import PREMIUM_PLAN, BASIC_PLAN, SUBSCRIPTION_STATUS_CHARGE_FAILED, SUBSCRIPTION_STATUS_ACTIVE, SUBSCRIPTION_STATUS_CANCELLED
from data_access import get_stripe_customer, find_user_by_id, update_user, delete_stripe_customer, \
  get_paystack_customer, User
from data_access.payment import get_payment_for_user, create_payment
from data_access.subscription import get_user_subscription, create_subscription, update_subscription
from exceptns import UserNotFoundException

logger = logging.getLogger(__name__)

class UserNotFoundError:
  pass


def __update_user(subscription: Subscription) -> [User, str]:
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
  user = find_user_by_id(customer.user_id)
  if user is None:
    raise UserNotFoundException("User not found")

  expiry = datetime.utcfromtimestamp(subscription["current_period_end"])
  update_user(user, {"tier": tier, "sub_expires_at": expiry})

  return user, tier

def handle_subscription_deleted(subscription: Subscription):
  customer = subscription["customer"]
  customer = get_stripe_customer(customer)
  if customer is not None:
    if user := find_user_by_id(customer.user_id):
      update_user(user, {"tier": None, "sub_expires_at": None})
      update_subscription(user_uuid=user.uuid, status=SUBSCRIPTION_STATUS_CANCELLED, provider="paystack")
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
      update_subscription(user_uuid=user.uuid, status=SUBSCRIPTION_STATUS_CANCELLED, provider="stripe")
    pass
  logger.info("Customer deleted")

def handle_stripe_subscription_creation(subscription: Subscription):
  user, tier = __update_user(subscription)
  create_subscription(user_uuid=user.uuid, plan=tier, provider='stripe',
                      next_subscription_at=subscription["current_period_end"])
  logger.info("Subscription created")


def handle_stripe_subscription_update(subscription: Subscription):
  user, tier = __update_user(subscription)
  update_subscription(user_uuid=user.uuid, status=SUBSCRIPTION_STATUS_ACTIVE, provider="stripe",
                      next_subscription_at=subscription["current_period_end"])

def handle_paystack_payment(transaction: dict):
  customer = get_paystack_customer(transaction["customer"]["customer_code"])
  if customer is None:
    raise UserNotFoundException("Paystack customer not found")
  user = find_user_by_id(customer.user_id)
  amount = transaction["amount"] / 100

  create_payment(user_uuid=user.uuid, amount=amount, currency=transaction["currency"], success="success", stripe_id=transaction["reference"])

def handle_paystack_new_subscription(subscription: dict):
  plan_code = subscription["plan"]["plan_code"]
  if plan_code == os.getenv("PAYSTACK_PREMIUM_PLAN_CODE"):
    tier = PREMIUM_PLAN
  elif plan_code == os.getenv("PAYSTACK_BASIC_PRICE_CODE"):
    tier = BASIC_PLAN
  else:
    raise RuntimeError("Invalid plan_code")

  customer = get_paystack_customer(subscription["customer"]["customer_code"])

  if customer is None:
    raise UserNotFoundException("Paystack customer not found")
  if user := find_user_by_id(customer.user_id):
    update_user(user, {"tier": tier, "sub_expires_at": subscription["next_payment_date"]})
    create_subscription(user_uuid=user.uuid, plan=tier, provider="paystack", next_subscription_at=subscription["next_payment_date"], status=SUBSCRIPTION_STATUS_ACTIVE)

def handle_paystack_subscription_event(subscription: dict):
  customer = subscription["customer"]["customer_code"]
  if subscription["status"] != "success":
    #payment for sub failed, switch to basic plan
    return handle_paystack_subscription_failure_or_cancelled(customer, SUBSCRIPTION_STATUS_CHARGE_FAILED, BASIC_PLAN)

  if subscription["plan_code"] == os.getenv("PAYSTACK_PREMIUM_PLAN_CODE"):
    tier = PREMIUM_PLAN
  elif subscription["plan_code"] == os.getenv("PAYSTACK_BASIC_PRICE_CODE"):
    tier = BASIC_PLAN
  else:
    raise RuntimeError("Invalid plan_code")

  logger.info(f"Subscription created for customer {customer}")
  _customer = get_paystack_customer(customer)
  if _customer is None:
    raise UserNotFoundException("Paystack customer not found")
  if user := find_user_by_id(_customer.user_id):
    update_user(user, {"tier": tier, "sub_expires_at": subscription["subscription"]["next_payment_date"]})
    update_subscription(user_uuid=user.uuid, status=SUBSCRIPTION_STATUS_ACTIVE, provider="paystack",
                        next_subscription_at=subscription["subscription"]["next_payment_date"])

  logger.info("Subscription created")

def handle_paystack_subscription_failure_or_cancelled(customer, status, tier=None):
  customer = get_paystack_customer(customer)
  if customer is None:
    raise UserNotFoundException("Paystack customer not found")
  user = find_user_by_id(customer.user_id)
  if user is None:
    raise UserNotFoundException("User not found")

  update_user(user, {"tier": tier, "sub_expires_at": None})
  update_subscription(user_uuid=user.uuid, status=status, provider="paystack")

def handle_expiring_cards(expiring_customer_cards, secret:str, paystack_url):
  for item in expiring_customer_cards:
    url = paystack_url + "/subscription/{}/manage/email".format(item["subscription"]["subscription_code"])
    #paystack sends email to customer with link to update card
    requests.post(url, headers={"Authorization": "Bearer {}".format(secret)})

