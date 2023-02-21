import logging
import os

import requests


MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
logger = logging.getLogger(__name__)

with open("util/static/welcome.html") as f:
  html_text = f.read()


def send_email(email: str):
  """Send email to user, use requests.post() to send email."""
  try:
    requests.post(
      "https://api.mailgun.net/v3/babs.ai/messages",
      auth=("api", MAILGUN_API_KEY),
      data={"from": "Babs <welcome@babs.ai>",
            "to": [email],
            "subject": "Hello from Babs",
            "html": html_text})

    # Add user to mailing list
    requests.post(
        "https://api.mailgun.net/v3/lists/welcome@babs.ai/members",
        auth=("api", MAILGUN_API_KEY),
        data={"subscribed": True,
              "address": [email]})
  except Exception as e:
    logger.error("Unable to send email.", e)


if __name__ == "__main__":
  send_email("temi.ayo.babs@gmail.com")
