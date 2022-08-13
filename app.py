import os

from util.app import create_app

if __name__ == '__main__':
  app = create_app()
  app.run(port=os.getenv('BABS_APP_PORT'))
