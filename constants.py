FREE_TRIAL = True
FREE_TRIAL_DAYS = 7
STRIPE_CHECKOUT_MODE = "subscription"

GOOGLE_MAIL_APP_NAME = "Google Mail"
GOOGLE_CAL_APP_NAME = "Google Calendar"

PREMIUM_PLAN = "premium"
BASIC_PLAN = "basic"
TRIAL_PLAN = "basic_trial"

CUSTOMER_SUBSCRIPTION_CREATED = "customer.subscription.created"
CUSTOMER_SUBSCRIPTION_UPDATED = "customer.subscription.updated"
CUSTOMER_SUBSCRIPTION_DELETED = "customer.subscription.deleted"
CUSTOMER_DELETED = "customer.deleted"

PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
PAYMENT_INTENT_FAILED = "payment_intent.payment_failed"

CONF_TYPE_CHANNEL = "channel"
CONF_TYPE_APP = "app"
DEFAULT_CHANNEL_CONFIG = "default"

BASE_SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email",
               "https://www.googleapis.com/auth/userinfo.profile"]
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

WHATSAPP_CHANNEL = "whatsapp"
TELEGRAM_CHANNEL = "telegram"
SLACK_CHANNEL = "slack"
