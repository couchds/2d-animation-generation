import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.utils.database import engine, Base
from app.models.animation import Animation, Frame

def check_animations_table():
    print("Checking animations table structure...")
    
    try:
        # Create a connection and inspect the database
        inspector = inspect(engine)
        
        # Check if the animations table exists
        if 'animations' not in inspector.get_table_names():
            print("Error: The 'animations' table doesn't exist in the database!")
            return False
            
        # Get the columns of the animations table
        existing_columns = {col['name'] for col in inspector.get_columns('animations')}
        print(f"Existing columns in animations table: {existing_columns}")
        
        # Get the columns from the Animation model
        model_columns = {column.name for column in Animation.__table__.columns}
        print(f"Expected columns from Animation model: {model_columns}")
        
        # Find missing columns
        missing_columns = model_columns - existing_columns
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            return missing_columns
        else:
            print("All columns exist in the animations table.")
            return set()
            
    except Exception as e:
        print(f"Error checking animations table: {str(e)}")
        return False

def fix_animations_table(missing_columns):
    print("\nFixing animations table...")
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                # Add each missing column
                for col_name in missing_columns:
                    # Get the column type from the model
                    column = Animation.__table__.columns[col_name]
                    sql_type = column.type.compile(dialect=engine.dialect)
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    
                    # Create ALTER TABLE statement
                    alter_sql = text(f"""
                    ALTER TABLE animations 
                    ADD COLUMN {col_name} {sql_type} {nullable};
                    """)
                    
                    print(f"Adding column {col_name} ({sql_type} {nullable})...")
                    connection.execute(alter_sql)
                
        print("Done fixing animations table!")
        return True
        
    except Exception as e:
        print(f"Error fixing animations table: {str(e)}")
        return False

def check_frames_table():
    print("\nChecking frames table structure...")
    
    try:
        # Create a connection and inspect the database
        inspector = inspect(engine)
        
        # Check if the frames table exists
        if 'frames' not in inspector.get_table_names():
            print("The 'frames' table doesn't exist in the database")
            return False
            
        # Get the columns of the frames table
        existing_columns = {col['name'] for col in inspector.get_columns('frames')}
        print(f"Existing columns in frames table: {existing_columns}")
        
        # Get the columns from the Frame model
        model_columns = {column.name for column in Frame.__table__.columns}
        print(f"Expected columns from Frame model: {model_columns}")
        
        # Find missing columns
        missing_columns = model_columns - existing_columns
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            return missing_columns
        else:
            print("All columns exist in the frames table.")
            return set()
            
    except Exception as e:
        print(f"Error checking frames table: {str(e)}")
        return False

def fix_frames_table(missing_columns):
    print("\nFixing frames table...")
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                # Add each missing column
                for col_name in missing_columns:
                    # Get the column type from the model
                    column = Frame.__table__.columns[col_name]
                    sql_type = column.type.compile(dialect=engine.dialect)
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    
                    # Create ALTER TABLE statement
                    alter_sql = text(f"""
                    ALTER TABLE frames 
                    ADD COLUMN {col_name} {sql_type} {nullable};
                    """)
                    
                    print(f"Adding column {col_name} ({sql_type} {nullable})...")
                    connection.execute(alter_sql)
                
        print("Done fixing frames table!")
        return True
        
    except Exception as e:
        print(f"Error fixing frames table: {str(e)}")
        return False

def recreate_tables():
    print("\nRecreating tables (WARNING: This will delete all data)...")
    
    try:
        # Drop all tables and recreate them
        with engine.connect() as connection:
            with connection.begin():
                # Drop tables if they exist
                connection.execute(text("DROP TABLE IF EXISTS frames CASCADE;"))
                connection.execute(text("DROP TABLE IF EXISTS animations CASCADE;"))
                print("Dropped existing tables.")
                
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print("Tables recreated successfully!")
        return True
    except Exception as e:
        print(f"Error recreating tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("Animation model tablename:", Animation.__tablename__)
    print("Frame model tablename:", Frame.__tablename__)
    
    # Check if tables match model definitions
    missing_in_animations = check_animations_table()
    missing_in_frames = check_frames_table()
    
    if missing_in_animations or missing_in_frames:
        print("\nThe database tables don't match the model definitions.")
        print("Option 1: Add missing columns (keeps existing data)")
        print("Option 2: Recreate tables (deletes all data)")
        
        choice = input("\nWhat would you like to do? (1/2): ")
        
        if choice == "1":
            if missing_in_animations:
                fix_animations_table(missing_in_animations)
            if missing_in_frames:
                fix_frames_table(missing_in_frames)
        elif choice == "2":
            confirm = input("Are you sure you want to delete all data? (yes/no): ")
            if confirm.lower() == "yes":
                recreate_tables()
        else:
            print("Invalid choice. No changes made.")
    else:
        print("\nTables match model definitions. No changes needed.") 