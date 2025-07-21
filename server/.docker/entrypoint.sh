#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to wait for the database to be ready
wait_for_db() {
    echo "Waiting for database to be ready..."

    
    # Wait for PostgreSQL to be ready
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
        echo "Database is unavailable - sleeping for 2 seconds..."
        sleep 2
    done
    
    echo "Database is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "Running Alembic database migrations..."
    cd /app
    ls
    # Run Alembic upgrade to latest migration
    alembic upgrade head
    
    echo "Database migrations completed successfully!"
}

# Main execution flow
main() {
    echo "=== FastAPI Application Startup ==="
    
    # Wait for database to be ready
    wait_for_db
    
    # Run database migrations
    run_migrations
    
}

main

exec "$@"