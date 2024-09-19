# Importing necessary modules and functions
from fastapi import FastAPI, HTTPException, Depends, status
from typing import  List, Optional, Annotated
from sqlalchemy.orm import Session
from typing import List

# Importing models for database operations    -----------------------FIX THIS SOMEHOW
from . import models
# Importing FlashcardBase from schemas for request and response handling
from .schemas import FlashcardBase, UserBase
# Importing engine and get_db from db for database session management
from .db import engine, get_db
# Importing auth route for authentication

from .auth import get_current_user
from router import auth_router, main_router


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(main_router)


'''
app.include_router(routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''