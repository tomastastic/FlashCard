## Pydantic models  
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


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
    created_at: datetime

    class Config:
        orm_mode = True