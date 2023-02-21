import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from util.app import create_app


if os.getenv("FLASK_CONFIG") in ["production", "staging"]:
  sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("FLASK_CONFIG"),
  )

app = create_app()


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=os.getenv('BABS_APP_PORT'))
