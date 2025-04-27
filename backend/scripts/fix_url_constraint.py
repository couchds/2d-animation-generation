import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.utils.database import engine, Base
from app.models.animation import Animation, Frame

def make_url_nullable():
    print("Modifying 'url' column in animations table to be nullable...")
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                # First check if url column exists
                inspector = inspect(engine)
                columns = {col['name'] for col in inspector.get_columns('animations')}
                
                if 'url' in columns:
                    # Make url column nullable
                    alter_sql = text("""
                    ALTER TABLE animations 
                    ALTER COLUMN url DROP NOT NULL;
                    """)
                    
                    connection.execute(alter_sql)
                    print("Modified 'url' column to be nullable.")
                else:
                    print("The 'url' column doesn't exist in the animations table.")
                
        return True
        
    except Exception as e:
        print(f"Error modifying url column: {str(e)}")
        return False

def drop_url_column():
    print("Dropping 'url' column from animations table...")
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                # Check if url column exists
                inspector = inspect(engine)
                columns = {col['name'] for col in inspector.get_columns('animations')}
                
                if 'url' in columns:
                    # Drop url column
                    alter_sql = text("""
                    ALTER TABLE animations 
                    DROP COLUMN url;
                    """)
                    
                    connection.execute(alter_sql)
                    print("Dropped 'url' column from animations table.")
                else:
                    print("The 'url' column doesn't exist in the animations table.")
                
        return True
        
    except Exception as e:
        print(f"Error dropping url column: {str(e)}")
        return False

def check_animations_table():
    print("Checking animations table structure...")
    
    try:
        inspector = inspect(engine)
        
        # Check if the animations table exists
        if 'animations' not in inspector.get_table_names():
            print("Error: The 'animations' table doesn't exist in the database!")
            return
            
        # Get the columns of the animations table
        columns = inspector.get_columns('animations')
        print("Columns in animations table:")
        for col in columns:
            print(f"- {col['name']} (Type: {col['type']}, Nullable: {col['nullable']})")
            
    except Exception as e:
        print(f"Error checking animations table: {str(e)}")

if __name__ == "__main__":
    print("Checking current table structure...")
    check_animations_table()
    
    print("\nYou have a 'url' column in the animations table that is causing problems.")
    print("Option 1: Make the 'url' column nullable (allows NULL values)")
    print("Option 2: Drop the 'url' column completely")
    
    choice = input("\nWhat would you like to do? (1/2): ")
    
    if choice == "1":
        make_url_nullable()
    elif choice == "2":
        drop_url_column()
    else:
        print("Invalid choice. No changes made.")
        
    print("\nFinal table structure:")
    check_animations_table() 