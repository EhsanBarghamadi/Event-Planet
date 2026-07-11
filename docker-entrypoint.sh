#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate

echo "Starting server..."
exec "$@"