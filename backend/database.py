from datetime import datetime
from typing import Generator

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Create declarative base for SQLAlchemy models
Base = declarative_base()


class ConversationDB(Base):  # type: ignore[valid-type,misc]
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    state = Column(String)
    prospect_data = Column(Text)  # JSON string
    messages = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Create engine and session
engine = create_engine("sqlite:///conversations.db", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
