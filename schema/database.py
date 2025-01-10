from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for PostgreSQL (Replace with your actual connection string)
DATABASE_URL = "postgresql://postgres:kshitij@localhost:5432/hackathon"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a Session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the ORM models
Base = declarative_base()

# Dependency for creating a new session instance
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
