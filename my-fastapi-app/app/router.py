# FILE: router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Annotated
from sqlalchemy.orm import Session
from auth import get_current_user, create_user, login_for_access_token, authenticate_user, create_access_token
from schemas import FlashcardBase, UserBase, CreateUserRequest, Token
from db import get_db
import models
# Create separate routers for auth and main routes
auth_router = APIRouter(prefix="/auth", tags=["auth"])
main_router = APIRouter(prefix="/main", tags=["main"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated [dict, Depends (get_current_user)]

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    return await create_user(db, create_user_request)

@auth_router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return await login_for_access_token(form_data, db)

@main_router.get("/flashcards", response_model=List[FlashcardBase])
def read_flashcards(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    flashcards = db.query(models.Flashcard).offset(skip).limit(limit).all()
    return flashcards

@main_router.get("/users", response_model=List[UserBase])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@main_router.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User": user}