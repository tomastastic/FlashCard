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

#User SQLAlchemy model for users
'''
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(16), unique=True, index=True)
    password = Column(String(64))
    email = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime)
'''