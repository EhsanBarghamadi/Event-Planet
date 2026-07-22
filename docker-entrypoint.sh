#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready and DNS to resolve..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT"; do
  echo "Database is unavailable - sleeping..."
  sleep 1
done

echo "Database is up and completely resolvable!"

echo "Running database migrations..."
python manage.py migrate

echo "Starting server..."
exec "$@"