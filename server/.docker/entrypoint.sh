#!/bin/bash

set -e

wait_for_db() {
    echo "Waiting for database to be ready..."

    DB_HOST=${DATABASE_HOST:-localhost}
    DB_PORT=${DATABASE_PORT:-5432}
    DB_NAME=${DATABASE_NAME:-giaithuat}
    DB_USER=${DATABASE_USER:-postgres}

    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
        echo "Database is unavailable - sleeping for 2 seconds..."
        sleep 2
    done

    echo "Database is ready!"
}

wait_for_db

echo "Running Alembic database migrations..."
alembic upgrade head
echo "Database migrations completed successfully!"

exec "$@"
