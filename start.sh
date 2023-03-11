#!/usr/bin/sh

# Start the server
SCRIPT_NAME=$BABS_VERSION gunicorn --bind 0.0.0.0:5000 --worker-class=sync --workers 9 --timeout 0 --preload app:app
