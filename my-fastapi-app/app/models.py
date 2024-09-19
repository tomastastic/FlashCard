from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLAlchemyEnum

from enum import Enum as PyEnum


Base = declarative_base()

# Enum for flashcard types 
class FlashcardType(PyEnum):
    kanji = "kanji"
    vocab = "vocab"
    radical = "radical"

# Flashcards models
class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, index=True)
    type = Column(SQLAlchemyEnum(FlashcardType), index=True)
    fields = Column(String(255))
    
    class Config:
        from_attributes = True
    

#User SQLAlchemy model for users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(16), unique=True, index=True)
    password = Column(String(64))
    email = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime)

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

####  CardSchedule model

class CardSchedule(Base):
    __tablename__ = "cardschedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    due = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    stability = Column(Float)
    difficulty = Column(Float)
    elapsed_days = Column(Integer)
    scheduled_days = Column(Integer)
    reps = Column(Integer)
    lapses = Column(Integer)
    state = Column(String(50))
    last_review = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    flashcard_id = Column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Define relationships (optional, based on use case)
    flashcard = relationship("Flashcard", back_populates="schedules")
    user = relationship("User", back_populates="schedules")

# Add these to the existing models for relationships
Flashcard.schedules = relationship("CardSchedule", back_populates="flashcard", cascade="all, delete-orphan")
User.schedules = relationship("CardSchedule", back_populates="user", cascade="all, delete-orphan")
