#!/bin/bash

# Exit on error
set -e

echo "Fixing PostgreSQL authentication..."

# Database configuration
DB_NAME="sprites_db"
DB_USER="sprites_user"

# Get the path to pg_hba.conf
PG_HBA_PATH=$(sudo -u postgres psql -t -P format=unaligned -c "SHOW hba_file;")

# Backup the original file
sudo cp "$PG_HBA_PATH" "${PG_HBA_PATH}.bak"

# Add our configuration
echo "Updating pg_hba.conf..."
sudo tee "$PG_HBA_PATH" << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

# Restart PostgreSQL
echo "Restarting PostgreSQL..."
sudo service postgresql restart

echo "PostgreSQL authentication fixed!"
echo "Try connecting with: psql -h localhost -U $DB_USER -d $DB_NAME" 