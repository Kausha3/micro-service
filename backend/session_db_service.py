"""
Database service for managing conversation sessions with SQLite persistence.
Provides CRUD operations for ConversationSession objects.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from database import SessionLocal, ConversationDB
from models import ConversationSession, ProspectData, ChatState, ConversationMessage

logger = logging.getLogger(__name__)


class SessionDatabaseService:
    """
    Service for persisting conversation sessions to SQLite database.
    Handles serialization/deserialization of Pydantic models to/from database.
    """

    def __init__(self):
        self.db_session_factory = SessionLocal

    def save_session(self, session: ConversationSession) -> bool:
        """
        Save or update a conversation session in the database.

        Args:
            session: ConversationSession object to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db = self.db_session_factory()

            # Check if session already exists
            existing = (
                db.query(ConversationDB)
                .filter(ConversationDB.id == session.session_id)
                .first()
            )

            # Serialize prospect_data and messages to JSON
            prospect_data_json = session.prospect_data.json()
            messages_json = json.dumps(
                [
                    {
                        "sender": msg.sender,
                        "text": msg.text,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                    for msg in session.messages
                ]
            )

            if existing:
                # Update existing session
                existing.state = session.state.value
                existing.prospect_data = prospect_data_json
                existing.messages = messages_json
                existing.updated_at = session.updated_at
            else:
                # Create new session
                db_session = ConversationDB(
                    id=session.session_id,
                    state=session.state.value,
                    prospect_data=prospect_data_json,
                    messages=messages_json,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                )
                db.add(db_session)

            db.commit()
            db.close()
            logger.info(f"Session {session.session_id} saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {str(e)}")
            if "db" in locals():
                db.rollback()
                db.close()
            return False

    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Load a conversation session from the database.

        Args:
            session_id: ID of the session to load

        Returns:
            ConversationSession object if found, None otherwise
        """
        try:
            db = self.db_session_factory()

            db_session = (
                db.query(ConversationDB).filter(ConversationDB.id == session_id).first()
            )

            if not db_session:
                db.close()
                return None

            # Deserialize prospect_data from JSON
            prospect_data = ProspectData.parse_raw(db_session.prospect_data)

            # Deserialize messages from JSON
            messages_data = json.loads(db_session.messages)
            messages = [
                ConversationMessage(
                    sender=msg["sender"],
                    text=msg["text"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                )
                for msg in messages_data
            ]

            # Create ConversationSession object
            session = ConversationSession(
                session_id=db_session.id,
                state=ChatState(db_session.state),
                prospect_data=prospect_data,
                messages=messages,
                created_at=db_session.created_at,
                updated_at=db_session.updated_at,
            )

            db.close()
            logger.info(f"Session {session_id} loaded successfully")
            return session

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {str(e)}")
            if "db" in locals():
                db.close()
            return None

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session from the database.

        Args:
            session_id: ID of the session to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db = self.db_session_factory()

            db_session = (
                db.query(ConversationDB).filter(ConversationDB.id == session_id).first()
            )

            if db_session:
                db.delete(db_session)
                db.commit()
                logger.info(f"Session {session_id} deleted successfully")
                result = True
            else:
                logger.warning(f"Session {session_id} not found for deletion")
                result = False

            db.close()
            return result

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            if "db" in locals():
                db.rollback()
                db.close()
            return False

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in the database.

        Args:
            session_id: ID of the session to check

        Returns:
            bool: True if session exists, False otherwise
        """
        try:
            db = self.db_session_factory()

            exists = (
                db.query(ConversationDB).filter(ConversationDB.id == session_id).first()
                is not None
            )

            db.close()
            return exists

        except Exception as e:
            logger.error(f"Failed to check session existence {session_id}: {str(e)}")
            if "db" in locals():
                db.close()
            return False


# Global instance
session_db_service = SessionDatabaseService()
