FREE_TRIAL = True
FREE_TRIAL_DAYS = 7
STRIPE_CHECKOUT_MODE = "subscription"

GOOGLE_MAIL_APP_NAME = "Google Mail"
GOOGLE_CAL_APP_NAME = "Google Calendar"
NOTION_APP_NAME = "Notion"

PREMIUM_PLAN = "premium"
FREE_PLAN = "free"
TRIAL_PLAN = "basic_trial"

STRIPE_CUSTOMER_SUBSCRIPTION_CREATED = "customer.subscription.created"
STRIPE_CUSTOMER_SUBSCRIPTION_UPDATED = "customer.subscription.updated"
STRIPE_CUSTOMER_SUBSCRIPTION_DELETED = "customer.subscription.deleted"
STRIPE_CUSTOMER_DELETED = "customer.deleted"

STRIPE_PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
STRIPE_PAYMENT_INTENT_FAILED = "payment_intent.payment_failed"

CONF_TYPE_CHANNEL = "channel"
CONF_TYPE_APP = "app"

DEFAULT_CONFIG = "default"

BASE_SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email",
               "https://www.googleapis.com/auth/userinfo.profile"]
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

WHATSAPP_CHANNEL = "whatsapp"
TELEGRAM_CHANNEL = "telegram"
SLACK_CHANNEL = "slack"
iMESSAGE_CHANNEL = "iMessage"

# successfully created new subscription
PAYSTACK_CUSTOMER_SUBSCRIPTION_CREATED = "subscription.create"
# payment was successful
PAYSTACK_CUSTOMER_CHARGE_SUCCESS = "charge.success"
# sent when charge attempt failed.
PAYSTACK_CUSTOMER_INVOICE_FAILED = "invoice.payment_failed"
# An invoice.update event will be sent after a subsequent charge attempt.
# This will contain the final status of the invoice for this subscription payment
PAYSTACK_CUSTOMER_INVOICE_UPDATE = "invoice.update"
# event will be sent to indicate that the subscription will not renew on the next payment date.
PAYSTACK_CUSTOMER_SUBSCRIPTION_NOT_RENEW = "subscription.not_renew"
# On the next payment date, a subscription.disable event will be sent to indicate that the subscription has been cancelled.
PAYSTACK_CUSTOMER_SUBSCRIPTION_DISABLED = "subscription.disable"
# sent at the beginning of each month, contains list of all subscriptions with cards that expire that month
PAYSTACK_SUBSCRIPTION_EXPIRING_CARDS = "subscription.expiring_cards"

SUBSCRIPTION_STATUS_ACTIVE = "active"
SUBSCRIPTION_STATUS_CHARGE_FAILED = "charge_failed"
SUBSCRIPTION_STATUS_NOT_RENEWING = "not_renewing"
SUBSCRIPTION_STATUS_CANCELLED = "cancelled"
