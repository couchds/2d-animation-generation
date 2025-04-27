import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.utils.database import engine

def update_db():
    print("Updating database schema...")
    
    try:
        # Create a connection
        with engine.connect() as connection:
            # Begin a transaction
            with connection.begin():
                # Check if the prompt column already exists
                check_column = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'frames' AND column_name = 'prompt';
                """)
                
                result = connection.execute(check_column)
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    # Add the prompt column if it doesn't exist
                    add_column = text("""
                    ALTER TABLE frames 
                    ADD COLUMN prompt TEXT;
                    """)
                    
                    connection.execute(add_column)
                    print("Added 'prompt' column to frames table.")
                else:
                    print("Column 'prompt' already exists in frames table.")
                
                # Check if duration column exists to be removed
                check_duration = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'frames' AND column_name = 'duration';
                """)
                
                result = connection.execute(check_duration)
                duration_exists = result.fetchone() is not None
                
                if duration_exists:
                    # Remove the duration column if it exists
                    drop_column = text("""
                    ALTER TABLE frames 
                    DROP COLUMN duration;
                    """)
                    
                    connection.execute(drop_column)
                    print("Removed 'duration' column from frames table.")
                else:
                    print("Column 'duration' doesn't exist in frames table.")
        
        print("Database schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        return False

if __name__ == "__main__":
    update_db() 