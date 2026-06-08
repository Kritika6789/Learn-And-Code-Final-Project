import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, SQLALCHEMY_DATABASE_URL

# Drop all tables and recreate them from the current models

def reset_db():
    # Create engine (same as in database.py)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    # Drop all existing tables
    Base.metadata.drop_all(bind=engine)
    # Create tables based on updated models
    Base.metadata.create_all(bind=engine)
    print("Database schema recreated from scratch.")

if __name__ == "__main__":
    reset_db()
