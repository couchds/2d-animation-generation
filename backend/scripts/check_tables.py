import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.utils.database import engine, Base

def check_tables():
    print("Checking database tables...")
    
    try:
        # Create a connection and inspect the database
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        print("Existing tables:")
        for table in table_names:
            print(f"- {table}")
            
            # Print columns for each table
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
                
        # Check if the model tables are created
        print("\nChecking model tables:")
        for table in Base.metadata.tables.keys():
            exists = table in table_names
            print(f"- {table}: {'Exists' if exists else 'Missing'}")
            
        return True
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        return False

def init_tables():
    print("\nInitializing database tables...")
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print("Tables initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing tables: {str(e)}")
        return False

if __name__ == "__main__":
    check_tables()
    
    # Ask if we should create the tables
    answer = input("\nDo you want to create missing tables? (y/n): ")
    if answer.lower() == 'y':
        init_tables()
        check_tables() 