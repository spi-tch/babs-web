import hashlib
import hmac
import json
import logging
import os

import requests
from paystackapi.paystack import Paystack

from constants import (PAYSTACK_CUSTOMER_CHARGE_SUCCESS,
                       PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED, PREMIUM_PLAN, FREE_PLAN,
                       PAYSTACK_CUSTOMER_INVOICE_UPDATE,
                       PAYSTACK_CUSTOMER_SUBSCRIPTION_NOT_RENEW,
                       PAYSTACK_CUSTOMER_SUBSCRIPTION_DISABLED, PAYSTACK_SUBSCRIPTION_EXPIRING_CARDS,
                       SUBSCRIPTION_STATUS_CANCELLED, SUBSCRIPTION_STATUS_NOT_RENEWING)
from data_access import PaystackCustomer, User, create_paystack_customer, get_paystack_customer_by_user_id
from services import BillingService
from util.handler import (handle_paystack_subscription_event, handle_paystack_payment,
                          handle_paystack_new_subscription,
                          handle_expiring_cards, handle_paystack_subscription_update)

PAYSTACK_BASE_URL = os.getenv('PAYSTACK_BASE_URL')
SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
PREMIUM_PLAN_CODE = os.getenv('PAYSTACK_PREMIUM_PLAN_CODE')
FREE_PLAN_CODE = os.getenv('PAYSTACK_FREE_PlAN_CODE')

paystack = Paystack(secret_key=SECRET_KEY)

logger = logging.getLogger(__name__)


class PayStackService(BillingService):

    @classmethod
    def create_checkout_session(cls, data, user: User):
        if data["plan"] == user.tier:
            return False, "Customer already subscribed to this plan", None

        if data["plan"] == PREMIUM_PLAN:
            plan_code = PREMIUM_PLAN_CODE
        elif data["plan"] == FREE_PLAN:
            plan_code = FREE_PLAN_CODE
        else:
            return False, "Invalid plan", None

        customer: PaystackCustomer = get_paystack_customer_by_user_id(user.id)
        if customer is None:
            paystack_response = paystack.customer.create(first_name=user.first_name, last_name=user.last_name,
                                                         email=user.email)
            create_paystack_customer(user.id, paystack_response["data"]['customer_code'])

            # initiate payment session
            # amount is required, however plan amount/price would override the amount passed.
            transaction = paystack.transaction.initialize(email=user.email, amount=10000, plan=plan_code)
            session = transaction["data"]
            if transaction["status"]:
                reference = session["reference"]  # where do we store ref? we (might) need it query transaction status
                return True, "Success", session["authorization_url"]
            else:
                logger.error(f"Paystack initiate tranaction failed. Paystack response : {session}")
                return False, "Payment initiation failed", None
        else:
            customer_subscriptions = cls.__get_active_subscription(user.id)
            if not customer_subscriptions:  # in case the user didn't complete the transaction the last time.
                transaction = paystack.transaction.initialize(email=user.email, amount=10000, plan=plan_code)
                session = transaction["data"]
                if transaction["status"]:
                    reference = session[
                        "reference"]  # where do we store ref? we (might) need it query transaction status
                    return True, "Success", session["authorization_url"]
            if len(customer_subscriptions) > 1:
                raise Exception("Customer has more than one active subscription")
            if len(customer_subscriptions) == 1:
                subscription = customer_subscriptions[0]
                # not entirely sure what to do here, there is no update subscription on paystack
                # disable sub, and create new.
                paystack.subscription.disable(code=subscription["subscription_code"], token=subscription["email_token"])
                # create new sub
                response = paystack.subscription.create(customer=customer.paystack_id, plan=plan_code,
                                                        authorization=subscription["authorization"][
                                                            "authorization_code"])
                if response["status"]:
                    return True, "Update has been requested", None
                logger.error(f"Unable to create subscription. Paystack response: {response}")
                return False, "Unable to complete subscription", None

    @classmethod
    def create_portal_session(cls, user: User):
        subscriptions = cls.__get_active_subscription(user.id)
        if len(subscriptions) == 0:
            return False, "No active savings", None
        if len(subscriptions) > 1:
            return False, "More than 1 active savings", None

        url = PAYSTACK_BASE_URL + "/subscription/{}/manage/link".format(subscriptions[0]["subscription_code"])
        generate_link = requests.get(url, headers={"Authorization": "Bearer {}".format(SECRET_KEY)})

        return True, "success", generate_link.json()["data"]["link"]

    @classmethod
    def handle_webhook(cls, request: str, signature: str):
        try:
            if not cls.__verify_signature(cls, request, signature):
                logger.error('⚠️ Webhook signature verification failed.')
                return False, f"Invalid signature: {signature}, request: {request}", None

            logger.warning(f"Paystack webhook received: {request}")

            _request = json.loads(request)
            data_object = _request["data"]

            try:
                if _request["event"] == PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED:
                    logger.info(f"PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED :{data_object}")
                    handle_paystack_new_subscription(data_object)
                elif _request["event"] == PAYSTACK_CUSTOMER_CHARGE_SUCCESS:
                    logger.info(f"PAYSTACK_CUSTOMER_CHARGE :{data_object}")
                    handle_paystack_payment(data_object)
                elif _request["event"] == PAYSTACK_CUSTOMER_SUBSCRIPTION_NOT_RENEW:
                    logger.info(f"PAYSTACK_CUSTOMER_SUBSCRIPTION_NOT_RENEW :{data_object}")
                    handle_paystack_subscription_update(data_object["customer"]["customer_code"],
                                                        SUBSCRIPTION_STATUS_NOT_RENEWING)
                elif _request["event"] == PAYSTACK_CUSTOMER_SUBSCRIPTION_DISABLED:
                    logger.info(f"PAYSTACK_CUSTOMER_SUBSCRIPTION_DISABLED :{data_object}")
                    handle_paystack_subscription_update(data_object["customer"]["customer_code"],
                                                        SUBSCRIPTION_STATUS_CANCELLED)
                elif _request["event"] == PAYSTACK_CUSTOMER_INVOICE_UPDATE:
                    subscription = paystack.subscription.fetch(data_object["subscription"]["subscription_code"])
                    data_object["plan_code"] = subscription["plan"]["plan_code"]
                    handle_paystack_subscription_event(data_object)
                elif _request["event"] == PAYSTACK_SUBSCRIPTION_EXPIRING_CARDS:
                    handle_expiring_cards(data_object, SECRET_KEY, PAYSTACK_BASE_URL)
            except Exception as e:
                logger.error(f"Error handling Stripe webhook: {e}")
                return False, f"Error handling Stripe webhook: {e}", None

        except ValueError as e:
            logger.error("Invalid payload on Paystack webhook")
            return False, f"Invalid payload: {e}", None
        except Exception as e:
            logger.error('⚠️ An unexpected error occurred.' + str(e))
            return False, f"An error occurred: {e}", None
        return True, "Success", None

    @classmethod
    def get_payment_status(cls, user_id):
        """"""

    def __verify_signature(cls, request: str, request_signature: str) -> bool:
        key = SECRET_KEY
        signature = hmac.new(key.encode(), request.encode(), hashlib.sha512).hexdigest()
        return signature == request_signature

    def __get_active_subscription(user_id: str):
        customer: PaystackCustomer = get_paystack_customer_by_user_id(user_id)
        if customer is None:
            raise Exception("Customer not found.")

        _customer = paystack.customer.get(customer.paystack_id)

        if _customer is None:
            raise Exception("Customer not found.")

        url = PAYSTACK_BASE_URL + "/subscription?customer=" + str(_customer["data"]["id"])
        subscriptions_response = requests.get(url, headers={"Authorization": "Bearer {}".format(SECRET_KEY)})
        subscriptions = subscriptions_response.json()["data"]

        return [sub for sub in subscriptions if sub["status"] == "active"]
