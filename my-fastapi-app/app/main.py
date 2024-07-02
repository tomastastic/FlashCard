# Importing necessary modules and functions
from fastapi import FastAPI, HTTPException, Depends, status
from typing import  List, Optional, Annotated
from sqlalchemy.orm import Session
from typing import List

# Importing models for database operations
import models 
# Importing FlashcardBase from schemas for request and response handling
from schemas import FlashcardBase, UserBase
# Importing SessionLocal and engine from db for database session management
from db import SessionLocal, engine
# Importing auth route for authentication
import auth
from auth import get_current_user

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

#Method get_db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated [dict, Depends (get_current_user)]

#Method get_db END

## API ENDPOINTS

# Flashcards
@app.get("/flashcards", response_model=List[FlashcardBase]) 
def read_flashcards(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    flashcards = db.query(models.Flashcard).offset(skip).limit(limit).all()
    return flashcards

# Users 
@app.get("/users", response_model=List[UserBase])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


#async def user(user: Optional[str] = Depends(user_dependency), db: Optional[str] = Depends(db_dependency)):
@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User": user}

'''
app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''