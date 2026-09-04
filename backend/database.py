from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Using SQLite for robust local development
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settle.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False is needed only for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to yield DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
