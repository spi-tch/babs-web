import logging

from abc import abstractmethod
from typing import Tuple
import stripe

from data_access import StripeCustomer, User, create_stripe_customer, get_stripe_customer_by_user_id
from data_access.payment import Payment


logger = logging.getLogger(__name__)


class BillingService:

  @abstractmethod
  def create_checkout_session(cls, data, user: User) -> Tuple[str, str, str]:
    """Create payment session, return payment url"""

  @abstractmethod
  def create_portal_session(cls, user: User):
    """Create portal session"""

  @classmethod
  def handle_webhook(cls, request: str, signature: str):
    """handle webhook requests from payment service provider"""

  def validate_plan(cls, plan: str) -> bool:
    """handle webhook requests from payment service provider"""
  @classmethod
  def get_payment_status(cls, user_id):
    try:
      customer = Payment.query.filter_by(user_uuid=user_id).first()
      subscription = stripe.Subscription.retrieve(customer.subscription_id)
      return True, "Success", subscription
    except Exception as e:
      return False, f"Unable to get payment status: {e}", None
