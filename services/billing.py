import logging
import os

import stripe
from stripe.api_resources.customer import Customer

from constants import FREE_TRIAL_DAYS, FREE_TRIAL, STRIPE_CHECKOUT_MODE
from data_access import StripeCustomer
from util.app import db

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

logger = logging.getLogger(__name__)


class BillingService:

  @classmethod
  def create_checkout_session(cls, data, user_id: int):
    customer = StripeCustomer.query.filter_by(user_id=user_id).first()
    if customer is None:
      customer: Customer = stripe.Customer.create()
      customer = StripeCustomer(
        user_id=user_id,
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

    if data["plan"] == "premium":
      price_id = os.getenv("STRIPE_PREMIUM_PRICE_ID")
    elif data["plan"] == "basic":
      price_id = os.getenv("STRIPE_BASIC_PRICE_ID")
    else:
      return False, "Invalid plan", None

    stripe_params = {
      "payment_method_types": ["card"],
      "line_items": [{"price": price_id, "quantity": 1}],
      "mode": STRIPE_CHECKOUT_MODE,
      "success_url": f"{os.getenv('FRONTEND_URL')}/app/settings",
      "cancel_url": f"{os.getenv('FRONTEND_URL')}/app/settings",
      "customer": customer.stripe_id
    }
    if FREE_TRIAL:
      stripe_params["subscription_data"] = {"trial_period_days": FREE_TRIAL_DAYS}

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
