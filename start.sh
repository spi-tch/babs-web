#!/usr/bin/sh

gunicorn --bind 0.0.0.0:5000 --worker-class=sync --workers 2 --timeout 0 --preload app:app
