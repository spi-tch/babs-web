import logging
import os
import json
import hashlib
import hmac

from paystackapi.paystack import Paystack
from constants import (PAYSTACK_CUSTOMER_CHARGE_SUCCESS,
                       PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED, PAYSTACK_CUSTOMER_INVOICE_CREATE, PREMIUM_PLAN, BASIC_PLAN,
                       PAYSTACK_CUSTOMER_INVOICE_FAILED, PAYSTACK_CUSTOMER_INVOICE_UPDATE, PAYSTACK_CUSTOMER_SUBSCRIPTION_NOT_RENEW,
                       PAYSTACK_CUSTOMER_SUBSCRIPTION_DISABLED)
from data_access import PaystackCustomer, User, create_paystack_customer, get_paystack_customer_by_user_id
from data_access.payment import Payment
from util.handler import (handle_paystack_subscription_payment_event, handle_subscription_deleted,
                          handle_paystack_subscription_failure_or_cancelled)

from services import BillingService

SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
PREMIUM_PLAN_CODE = os.getenv('PAYSTACK_PREMIUM_PLAN_CODE')
BASIC_PLAN_CODE = os.getenv('PAYSTACK_BASIC_PRICE_CODE')

paystack = Paystack(secret_key=SECRET_KEY)

logger = logging.getLogger(__name__)


class PayStackService(BillingService):

  @classmethod
  def create_checkout_session(cls, data, user: User):
    if data["plan"] == user.tier:
          return False, "Customer already subscribed to this plan", None

    if data["plan"] == PREMIUM_PLAN:
      plan_code = PREMIUM_PLAN_CODE
    elif data["plan"] == BASIC_PLAN:
      plan_code = BASIC_PLAN_CODE
    else:
      return False, "Invalid plan", None

    customer: PaystackCustomer = get_paystack_customer_by_user_id(user.id)
    if customer is None:
      paystack_response = paystack.customer.create(first_name=user.first_name,last_name=user.last_name,email=user.email)
      create_paystack_customer(user.id, paystack_response["data"]['customer_code'])

      #initiate payment session
      #amount is required, however plan amount/price would override the amount passed.
      transaction = paystack.transaction.initialize(email=user.email, amount=10000, plan=plan_code)
      session = transaction["data"]
      if transaction["status"]:
        reference = session["reference"] #where do we store ref? we (might) need it query transaction status
        return True, "Success", session["authorization_url"]
      else:
        logger.error(f"Paystack initiate tranaction failed. Paystack response : {session}")
        return False, "Payment initiation failed", None
    else:
      subscriptions_response = paystack.subscription.list()
      subscriptions = subscriptions_response["data"]
      customer_subscriptions = [sub for sub in subscriptions if sub["customer"]["customer_code"] == customer.paystack_id and sub["status"] == "active"]
      if len(customer_subscriptions) > 1:
        raise Exception("Customer has more than one active subscription")
      if len(customer_subscriptions) == 1:
        subscription = customer_subscriptions[0]
        #not entirely sure what to do here, there is no update subscription on paystack
        #disable sub, and create new.
        paystack.subscription.disable(code=subscription["subscription_code"], token=subscription["email_token"])
        #create new sub
        response = paystack.subscription.create(customer=customer.paystack_id, plan=plan_code, authorization=subscription["authorization"]["authorization_code"])
        if response["status"]:
          return True, "Update has been requested", None
        logger.error(f"Unable to create subscription. Paystack response: {response}")
        return False, "Unable to complete subscription", None


  @classmethod
  def create_portal_session(cls, user: User):
    """"""

  @classmethod
  def handle_webhook(cls, request: str, signature: str):
    try:
      if not cls.__verify_signature(request, signature):
        logger.error('⚠️ Webhook signature verification failed.')
        return False, f"Invalid signature: {signature}, request: {request}", None

      logger.warning(f"Paystack webhook received: {request}")

      _request = json.loads(request)
      data_object = _request["data"]

      try:
        if _request["event"] == PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED:
          logger.debug(f"PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED :{data_object}")
        elif _request["event"] == PAYSTACK_CUSTOMER_CHARGE_SUCCESS:
          logger.debug(f"PAYSTACK_CUSTOMER_CHARGE_SUCCESS :{data_object}")
        elif _request["event"] == PAYSTACK_CUSTOMER_SUBSCRIPTION_DISABLED:
          handle_paystack_subscription_failure_or_cancelled(data_object)
        elif _request["event"] == PAYSTACK_CUSTOMER_INVOICE_UPDATE:
          #fetch sub details
          subscription = paystack.subscription.fetch(data_object["subscription"]["subscription_code"])
          handle_paystack_subscription_payment_event(data_object["status"], subscription["plan"]["plan_code"],
                                                     data_object["customer"]["customer_code"], data_object["next_payment_date"],
                                                     data_object["amount"], data_object["transaction"]["reference"])
          logger.info("Subscription deleted")
        elif _request["event"] == PAYSTACK_CUSTOMER_INVOICE_FAILED:
          handle_paystack_subscription_failure_or_cancelled(data_object, BASIC_PLAN)
          logger.info("Got payment intent info")
      except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        return False, f"Error handling Stripe webhook: {e}", None

    except ValueError as e:
      logger.error("Invalid payload on Stripe webhook")
      return False, f"Invalid payload: {e}", None
    except Exception as e:
      logger.error('⚠️ An unexpected error occurred.' + str(e))
      return False, f"An error occurred: {e}", None
  @classmethod
  def get_payment_status(cls, user_id):
    """"""
  def __verify_signature(cls, request: str, request_signature: str) -> bool:
    key = SECRET_KEY
    signature = hmac.new(key.encode(), request.encode(), hashlib.sha512).hexdigest()
    return signature == request_signature

