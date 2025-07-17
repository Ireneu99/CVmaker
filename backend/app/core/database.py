from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import os

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(settings.database_url.replace("sqlite:///", "")), exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_tables():
    from backend.app.models import Base, User, CV, Log
    
    Base.metadata.create_all(bind=engine)
