#!/bin/bash

# Exit on error
set -e

echo "Cleaning up PostgreSQL..."

# Database configuration
DB_NAME="sprites_db"
DB_USER="sprites_user"

# Drop the database if it exists
echo "Dropping database..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"

# Drop the user if it exists
echo "Dropping user..."
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;"

# Restart PostgreSQL to ensure clean state
echo "Restarting PostgreSQL..."
sudo service postgresql restart

echo "Cleanup complete!" 