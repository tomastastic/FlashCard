from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(16), unique=True, index=True)
    password = Column(String(64))
    email = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(255))
    owner_id = Column(Integer)