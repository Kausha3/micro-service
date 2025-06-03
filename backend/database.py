from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class ConversationDB(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    state = Column(String)
    prospect_data = Column(Text)  # JSON string
    messages = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Create engine and session
engine = create_engine('sqlite:///conversations.db', echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
