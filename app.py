import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from util.app import create_app


sentry_sdk.init(
  dsn="https://f07103f27c074f2aa59a469446d53bdb@o1379990.ingest.sentry.io/6693095",
  integrations=[FlaskIntegration()],
  traces_sample_rate=1.0
)

app = create_app()


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=os.getenv('BABS_APP_PORT'))
