from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import  List, Optional, Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from uuid import UUID, uuid4 #i dont need this?

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

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
## Pydantic schemas END


#Method get_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
#Method get_db END

## API ENDPOINTS
# READ 10 flashcards

@app.get("/flashcards", response_model=List[models.Flashcard])
def read_flashcards(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    flashcards = db.query(models.Flashcard).offset(skip).limit(limit).all()
    return flashcards



'''
app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''