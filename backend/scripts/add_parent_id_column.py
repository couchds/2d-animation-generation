from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

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

# Add parent_id and edit_description columns if they don't exist
with engine.connect() as connection:
    # Check if parent_id column exists
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sprites' AND column_name='parent_id'
    """))
    parent_id_exists = result.fetchone() is not None

    # Check if edit_description column exists
    result = connection.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sprites' AND column_name='edit_description'
    """))
    edit_description_exists = result.fetchone() is not None

    # Add parent_id column if it doesn't exist
    if not parent_id_exists:
        connection.execute(text("""
            ALTER TABLE sprites ADD COLUMN parent_id VARCHAR REFERENCES sprites(id) NULL
        """))
        connection.commit()
        print("Successfully added parent_id column to sprites table")
    else:
        print("parent_id column already exists in sprites table")
    
    # Add edit_description column if it doesn't exist
    if not edit_description_exists:
        connection.execute(text("""
            ALTER TABLE sprites ADD COLUMN edit_description TEXT NULL
        """))
        connection.commit()
        print("Successfully added edit_description column to sprites table")
    else:
        print("edit_description column already exists in sprites table")

print("Migration complete!") 