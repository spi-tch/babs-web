import logging
import os

import stripe
from flask import Blueprint, request
from stripe.error import SignatureVerificationError

payment = Blueprint("payment", __name__)

logger = logging.getLogger(__name__)


# Create endpoints for payments, use Stripe's API
# https://stripe.com/docs/api
@payment.route("/payment", methods=["POST"])
def payment():
    data = request.json
    try:
        stripe.api_key = os.getenv("STRIPE_SECRET")
        event = stripe.Event.construct_from(
            data, stripe.api_key
        )
        # Handle the event
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            # Then define and call a method to handle the successful payment intent.
            # handle_payment_intent_succeeded(payment_intent)
        elif event.type == "payment_method.attached":
            payment_method = event.data.object
            # Then define and call a method to handle the successful attachment of a PaymentMethod.
            # handle_payment_method_attached(payment_method)
        # ... handle other event types
        else:
            # Unexpected event type
            logger.error(f"Unexpected event type {event.type}")
    except SignatureVerificationError as e:
        # Invalid signature
        logger.error(e)
        return {"error": "Invalid signature", "success": False}, 400
    except Exception as e:
        logger.error(e)
        return {"error": "Something Happened", "success": False}, 500

    return {"message": "Payment successful", "success": True}, 200


@payment.route("/payment", methods=["GET"])
def get_payment():
    try:
        stripe.api_key = os.getenv("STRIPE_SECRET")
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,
            currency="usd",
            payment_method_types=["card"],
        )
        return {"message": "Payment successful", "success": True}, 200
    except Exception as e:
        logger.error(e)
        return {"error": "Something Happened", "success": False}, 500




# Setup a stripe webhook
@payment.route("/webhook", methods=["POST"])
def webhook():
  payload = request.data
  sig_header = request.headers.get("Stripe-Signature")

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
    )
  except ValueError as e:
    logger.error(e)
    return {"error": "Invalid payload"}, 400
  except SignatureVerificationError as e:
    logger.error(e)
    return {"error": "Invalid signature"}, 400


