import os

from util.app import create_app

app = create_app()


if __name__ == '__main__':
  app.run(port=os.getenv('BABS_APP_PORT'))
