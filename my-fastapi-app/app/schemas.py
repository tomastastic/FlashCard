from pydantic import BaseModel, EmailStr

from enum import Enum
from datetime import datetime
from typing import Optional

# Pydantic models for request and response handling
class FlashcardType(str, Enum):
    kanji = "kanji"
    vocab = "vocab"
    radical = "radical"

class FlashcardBase(BaseModel):
    id: int
    level: int
    type: FlashcardType
    fields: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: int
    username: str
    password: str
    email: str
    created_at: Optional[datetime] = None
    class Config:
        orm_mode = True

class CreateUserRequest(BaseModel):         
    username: str
    password: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

####  CardSchedule model

# Pydantic schema for CardSchedule
class CardSchedule(BaseModel):
    id: Optional[int]
    due: Optional[datetime]
    stability: Optional[float]
    difficulty: Optional[float]
    elapsed_days: Optional[int]
    scheduled_days: Optional[int]
    reps: Optional[int]
    lapses: Optional[int]
    state: Optional[str]
    last_review: Optional[datetime]
    flashcard_id: Optional[int]
    user_id: Optional[int]

    class Config:
        orm_mode = True


##### Move to schemas.py if succesful
from enum import Enum, IntEnum
from typing import List, Annotated

"""class Rating(str, Enum):
    Again = "Again"
    Hard = "Hard"
    Good = "Good"
    Easy = "Easy
"""
class FlashcardRating(BaseModel):
    flashcard_id: int
    rating: str

class FlashcardRatingList(BaseModel):
    ratings: FlashcardRating

##### Move to schemas.py if succesful