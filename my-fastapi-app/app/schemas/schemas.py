## Pydantic models  
from pydantic import BaseModel
from enum import Enum

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
