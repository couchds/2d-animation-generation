#!/bin/bash

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "Error: Virtual environment not found. Please create it first."
    exit 1
fi

# Initialize the database
echo "Initializing database..."
python -c "from app.utils.database import init_db; init_db()"

if [ $? -eq 0 ]; then
    echo "Database initialized successfully!"
else
    echo "Error: Failed to initialize database."
    exit 1
fi 