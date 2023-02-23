import logging
import os

import stripe
from stripe.api_resources.customer import Customer
from stripe.error import SignatureVerificationError

from constants import (STRIPE_CHECKOUT_MODE, CUSTOMER_SUBSCRIPTION_DELETED,
                       CUSTOMER_SUBSCRIPTION_CREATED, CUSTOMER_SUBSCRIPTION_UPDATED, PREMIUM_PLAN, BASIC_PLAN)
from data_access import StripeCustomer, User
from util.app import db
from util.handler import handle_subscription_created_or_updated, handle_subscription_deleted

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
PREMIUM_PRICE_ID = os.getenv("STRIPE_PREMIUM_PRICE_ID")
BASIC_PRICE_ID = os.getenv("STRIPE_BASIC_PRICE_ID")

logger = logging.getLogger(__name__)


class BillingService:

  @classmethod
  def create_checkout_session(cls, data, user: User):
    if data["plan"] == user.tier:
      return False, "Customer already subscribed to this plan", None

    if data["plan"] == PREMIUM_PLAN:
      price_id = PREMIUM_PRICE_ID
    elif data["plan"] == BASIC_PLAN:
      price_id = BASIC_PRICE_ID
    else:
      return False, "Invalid plan", None

    customer = StripeCustomer.query.filter_by(user_id=user.id).first()
    if customer is None:
      customer: "Customer" = stripe.Customer.create(email=user.email)
      customer: StripeCustomer = StripeCustomer(
        user_id=user.id,
        stripe_id=customer.id
      )
      try:
        db.session.add(customer)
        db.session.commit()
      except Exception as e:
        logger.error(e)
        db.session.rollback()
      finally:
        db.session.close()
    else:
      subscriptions = stripe.Subscription.list(customer=customer.stripe_id, status="active", limit=1)
      if len(subscriptions["data"]) > 1:
        raise Exception("Customer has more than one active subscription")
      subscription = subscriptions["data"][0]
      stripe.Subscription.modify(
        subscription["id"],
        proration_behavior="always_invoice",
        items=[{
          "id": subscription["items"]["data"][0]["id"],
          "price": price_id
        }]
      )

      return False, "Updated has been requested", None

    stripe_params = {
      "payment_method_types": ["card"],
      "line_items": [{"price": price_id, "quantity": 1}],
      "mode": STRIPE_CHECKOUT_MODE,
      "success_url": f"{os.getenv('FRONTEND_URL')}/app/settings",
      "cancel_url": f"{os.getenv('FRONTEND_URL')}/app/settings",
      "customer": customer.stripe_id,
      "payment_behavior": "default_incomplete"
    }

    # no need for this because we're not using the trial from Stripe
    #   if FREE_TRIAL:
    #     stripe_params["subscription_data"] = {"trial_period_days": FREE_TRIAL_DAYS}

    try:
      session = stripe.checkout.Session.create(**stripe_params)
      return True, "Success", session
    except Exception as e:
      return False, f"Unable to create subscription: {e}", None

  @classmethod
  def create_portal_session(cls, user_id):
    try:
      customer = StripeCustomer.query.filter_by(user_id=user_id).first()
      session = stripe.billing_portal.Session.create(
        customer=customer.stripe_id,
        return_url=os.getenv("FRONTEND_URL")
      )
      return True, "Success", session
    except Exception as e:
      return False, f"Unable to create portal session: {e}", None

  @classmethod
  def get_cards(cls, user_id):
    try:
      customer = StripeCustomer.query.filter_by(user_id=user_id).first()
      cards = stripe.Customer.list_sources(
        id=customer.stripe_id,
        object="card",
        limit=3
      )
      return True, "Success", cards
    except Exception as e:
      return False, f"Unable to get cards: {e}", None

  @classmethod
  def handle_stripe_webhook(cls, data: bytes, signature: str):
    try:
      event = stripe.Webhook.construct_event(data, signature, os.getenv("STRIPE_WEBHOOK_SECRET"))
    except ValueError as e:
      logger.error("Invalid payload on Stripe webhook")
      return False, f"Invalid payload: {e}", None
    except SignatureVerificationError as e:
      logger.error('⚠️ Webhook signature verification failed.' + str(e))
      return False, f"Invalid signature: {e}", None

    logger.warning(f"Stripe webhook received: {event['type']}")

    data_object = event["data"]["object"]
    if event["type"] == CUSTOMER_SUBSCRIPTION_CREATED or event["type"] == CUSTOMER_SUBSCRIPTION_UPDATED:
      handle_subscription_created_or_updated(data_object)
    elif event["type"] == CUSTOMER_SUBSCRIPTION_DELETED:
      handle_subscription_deleted(data_object)
      logger.info("Subscription deleted")
    elif event["type"] == "invoice.payment_succeeded":
      logger.info("Subscription updated")

    return True, "Success", None

  @classmethod
  def cancel_subscription(cls, user_id):
    try:
      customer = StripeCustomer.query.filter_by(user_id=user_id).first()
      stripe.Subscription.delete(customer.subscription_id)
      return True, "Success", None
    except Exception as e:
      return False, f"Unable to cancel subscription: {e}", None
