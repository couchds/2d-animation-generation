import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.utils.database import engine, Base, init_db
from app.models.animation import Animation, Frame
from app.models.sprite import Sprite

def print_models():
    print("\nRegistered models in SQLAlchemy metadata:")
    for table_name, table in Base.metadata.tables.items():
        print(f"- {table_name}")
        # Print columns for each model
        for column in table.columns:
            print(f"  - {column.name} ({column.type})")

def check_tables():
    print("\nChecking existing tables in database:")
    
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
        print("\nChecking model tables against database:")
        for table in Base.metadata.tables.keys():
            exists = table in table_names
            print(f"- {table}: {'Exists' if exists else 'Missing'}")
            
        return True
    except Exception as e:
        print(f"Error checking database: {str(e)}")
        return False

def initialize_tables():
    print("\nInitializing all tables in the database...")
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("Tables initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("Animation model tablename:", Animation.__tablename__)
    print("Frame model tablename:", Frame.__tablename__)
    print("Sprite model tablename:", Sprite.__tablename__)
    
    print_models()
    check_tables()
    
    # Ask if we should create/update the tables
    answer = input("\nDo you want to create/update the tables? (y/n): ")
    if answer.lower() == 'y':
        initialize_tables()
        check_tables() 