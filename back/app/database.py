from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    """Yields a database session, and always closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()