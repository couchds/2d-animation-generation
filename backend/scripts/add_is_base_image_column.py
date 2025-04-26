from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, Boolean, DateTime
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Validate required parameters
required_params = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_NAME": DB_NAME
}

missing_params = [param for param, value in required_params.items() if not value]
if missing_params:
    raise ValueError(f"Missing required database parameters: {', '.join(missing_params)}")

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the sprites table
sprites_table = Table(
    'sprites',
    metadata,
    Column('id', String, primary_key=True),
    Column('url', String, nullable=False),
    Column('description', Text, nullable=False),
    Column('is_base_image', Boolean, default=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, onupdate=datetime.utcnow)
)

# Create all tables
metadata.create_all(engine)
print("Successfully created sprites table")

# Add is_base_image column if it doesn't exist
with engine.connect() as connection:
    # Check if the column exists
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sprites' AND column_name='is_base_image'
    """))
    column_exists = result.fetchone() is not None

    if not column_exists:
        # Add the column
        connection.execute(text("""
            ALTER TABLE sprites ADD COLUMN is_base_image BOOLEAN DEFAULT TRUE
        """))
        connection.commit()
        print("Successfully added is_base_image column to sprites table")
    else:
        print("is_base_image column already exists in sprites table") 