import logging
import os

import requests


MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
logger = logging.getLogger(__name__)


def send_email(email: str):
  """Send email to user, use requests.post() to send email."""
  try:
    requests.post(
      "https://api.mailgun.net/v3/babs.ai/messages",
      auth=("api", MAILGUN_API_KEY),
      data={"from": "Babs <admin@babs.ai>",
            "to": [email],
            "subject": "Hello from Babs",
            "html": "Testing Babs mailing!"})
  except Exception as e:
    logger.error("Unable to send email.", e)

