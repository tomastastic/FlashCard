# Importing necessary modules and functions
from fastapi import FastAPI, HTTPException, Depends, status
from typing import  List, Optional, Annotated
from sqlalchemy.orm import Session
from typing import List

# Importing models for database operations
import models 
# Importing FlashcardBase from schemas for request and response handling
from schemas import FlashcardBase
# Importing SessionLocal and engine from db for database session management
from db import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


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


@app.get("/flashcards", response_model=List[FlashcardBase]) 
def read_flashcards(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    flashcards = db.query(models.Flashcard).offset(skip).limit(limit).all()
    return flashcards



'''
app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''