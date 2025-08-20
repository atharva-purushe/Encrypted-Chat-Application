from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from datetime import datetime
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # ✅ stored as string (hashed password)

    def __repr__(self):
        return f"<User(username={self.username!r})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, index=True, nullable=False)
    sender = Column(String, index=True, nullable=False)
    content_ciphertext = Column(LargeBinary, nullable=False)  # ✅ encrypted bytes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Message(room={self.room!r}, sender={self.sender!r})>"
