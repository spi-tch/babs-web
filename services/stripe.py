import logging
import os

import stripe
from stripe.api_resources.customer import Customer
from stripe.error import SignatureVerificationError

from constants import (STRIPE_CHECKOUT_MODE, STRIPE_CUSTOMER_SUBSCRIPTION_DELETED,
                       STRIPE_CUSTOMER_SUBSCRIPTION_CREATED, STRIPE_CUSTOMER_SUBSCRIPTION_UPDATED, PREMIUM_PLAN,
                       FREE_PLAN,
                       STRIPE_PAYMENT_INTENT_SUCCEEDED, STRIPE_PAYMENT_INTENT_FAILED, STRIPE_CUSTOMER_DELETED)
from data_access import StripeCustomer, User, create_stripe_customer, get_stripe_customer_by_user_id
from data_access.payment import Payment
from util.handler import (handle_subscription_deleted,
                          handle_payment_success_or_failure, handle_customer_deleted,
                          handle_stripe_subscription_creation,
                          handle_stripe_subscription_update)

from services import BillingService

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
PREMIUM_PRICE_ID = os.getenv("STRIPE_PREMIUM_PRICE_ID")
FREE_PRICE_ID = os.getenv("STRIPE_BASIC_PRICE_ID")

logger = logging.getLogger(__name__)


class StripeService(BillingService):

    @classmethod
    def create_checkout_session(cls, data, user: User):
        if data["plan"] == user.tier:
            return False, "Customer already subscribed to this plan", None

        if data["plan"] == PREMIUM_PLAN:
            price_id = PREMIUM_PRICE_ID
        elif data["plan"] == FREE_PLAN:
            price_id = FREE_PRICE_ID
        else:
            return False, "Invalid plan", None

        customer: StripeCustomer = get_stripe_customer_by_user_id(user.id)
        if customer is None:
            customer: "Customer" = stripe.Customer.create(email=user.email)
            create_stripe_customer(user.id, customer.id)
        else:
            subscriptions = stripe.Subscription.list(customer=customer.stripe_id, status="active", limit=1)
            if len(subscriptions["data"]) > 1:
                raise Exception("Customer has more than one active subscription")
            if len(subscriptions["data"]) == 1:
                subscription = subscriptions["data"][0]
                stripe.Subscription.modify(
                    subscription["id"],
                    proration_behavior="always_invoice",
                    items=[{
                        "id": subscription["items"]["data"][0]["id"],
                        "price": price_id
                    }]
                )

            # return True, "Update has been requested", None

        stripe_params = {
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": STRIPE_CHECKOUT_MODE,
            "success_url": f"{os.getenv('FRONTEND_URL')}/app/settings?tab=subscription",
            "cancel_url": f"{os.getenv('FRONTEND_URL')}/app/settings?tab=subscription",
            "customer": customer.stripe_id
        }

        # no need for this because we're not using the trial from Stripe
        #   if FREE_TRIAL:
        #     stripe_params["subscription_data"] = {"trial_period_days": FREE_TRIAL_DAYS}

        try:
            session = stripe.checkout.Session.create(**stripe_params)
            return True, "Success", session.url
        except Exception as e:
            return False, f"Unable to create subscription: {e}", None

    @classmethod
    def create_portal_session(cls, user: User):
        try:
            customer: "StripeCustomer" = get_stripe_customer_by_user_id(user_id=user.id)
            if not customer:
                customer: "Customer" = stripe.Customer.create(email=user.email)
                create_stripe_customer(user.id, customer.id)
                customer_stripe_id = customer.id
            else:
                customer_stripe_id = customer.stripe_id
            session = stripe.billing_portal.Session.create(
                customer=customer_stripe_id,
                return_url=os.getenv("FRONTEND_URL")
            )
            return True, "Success", session.url
        except Exception as e:
            return False, f"Unable to create portal session: {e}", None

    @classmethod
    def handle_webhook(cls, request: str, signature: str):
        try:
            event = stripe.Webhook.construct_event(request, signature, os.getenv("STRIPE_WEBHOOK_SECRET"))
        except ValueError as e:
            logger.error("Invalid payload on Stripe webhook")
            return False, f"Invalid payload: {e}", None
        except SignatureVerificationError as e:
            logger.error('⚠️ Webhook signature verification failed.' + str(e))
            return False, f"Invalid signature: {e}", None

        logger.warning(f"Stripe webhook received: {event['type']}")

        data_object = event["data"]["object"]
        try:
            if event["type"] == STRIPE_CUSTOMER_SUBSCRIPTION_CREATED:
                handle_stripe_subscription_creation(data_object)
            elif event["type"] == STRIPE_CUSTOMER_SUBSCRIPTION_UPDATED:
                handle_stripe_subscription_update(data_object)
                logger.info("Subscription updated")
            elif event["type"] == STRIPE_CUSTOMER_SUBSCRIPTION_DELETED:
                handle_subscription_deleted(data_object)
                logger.info("Subscription deleted")
            elif event["type"] == STRIPE_PAYMENT_INTENT_SUCCEEDED or event["type"] == STRIPE_PAYMENT_INTENT_FAILED:
                handle_payment_success_or_failure(data_object)
                logger.info("Got payment intent info")
            elif event["type"] == STRIPE_CUSTOMER_DELETED:
                handle_customer_deleted(data_object)
                logger.info("Customer deleted")
        except Exception as e:
            logger.error(f"Error handling Stripe webhook: {e}")
            return False, f"Error handling Stripe webhook: {e}", None

        return True, "Success", None

    @classmethod
    def get_payment_status(cls, user_id):
        try:
            customer = Payment.query.filter_by(user_uuid=user_id).first()
            subscription = stripe.Subscription.retrieve(customer.subscription_id)
            return True, "Success", subscription
        except Exception as e:
            return False, f"Unable to get payment status: {e}", None
