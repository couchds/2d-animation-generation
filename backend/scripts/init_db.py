import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.database import init_db, Base, engine
from app.models.sprite import Sprite
from app.models.animation import Animation

def main():
    print("Initializing database...")
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    main() 