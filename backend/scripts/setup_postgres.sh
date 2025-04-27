#!/bin/bash

# Exit on error
set -e

echo "Setting up PostgreSQL for local development..."

# Database configuration
DB_NAME="sprites_db"
DB_USER="sprites_user"
DB_PASSWORD="sprites_password"

# Start PostgreSQL service if not running
if ! pg_isready -h localhost -p 5432; then
    echo "Starting PostgreSQL service..."
    sudo service postgresql start
fi

# Create user if not exists
echo "Creating database user..."
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# Create database if not exists
echo "Creating database..."
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres createdb -O $DB_USER $DB_NAME

# Grant privileges
echo "Granting privileges..."
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;"

# Update pg_hba.conf to allow local connections
echo "Updating PostgreSQL authentication configuration..."
PG_HBA_PATH=$(sudo -u postgres psql -t -P format=unaligned -c "SHOW hba_file;")

# Check if the configuration already exists
if ! sudo grep -q "local   $DB_NAME      $DB_USER" "$PG_HBA_PATH"; then
    echo "# Local connections for $DB_USER" | sudo tee -a "$PG_HBA_PATH" > /dev/null
    echo "local   $DB_NAME      $DB_USER                            md5" | sudo tee -a "$PG_HBA_PATH" > /dev/null
    echo "host    $DB_NAME      $DB_USER      127.0.0.1/32         md5" | sudo tee -a "$PG_HBA_PATH" > /dev/null
    
    # Restart PostgreSQL to apply changes
    echo "Restarting PostgreSQL..."
    sudo service postgresql restart
fi

echo "PostgreSQL setup complete!"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD" 