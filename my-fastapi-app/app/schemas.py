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