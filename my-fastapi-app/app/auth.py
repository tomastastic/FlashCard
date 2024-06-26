from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException 
from pydantic import BaseModel 
from sqlalchemy.orm import Session 
from starlette import status 
from db import SessionLocal 
from models import User 
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
SECRET_KEY = "secret"
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):         #might need to fix the data types
    username: str
    password: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

def getdb():                                #should this be here? can i import it from main.py?
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(getdb)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = User(
        username=create_user_request.username,
        password=bcrypt_context.hash(create_user_request.password),
        email=create_user_request.email,
        created_at=datetime.now(),
    )
    db.add(create_user_model)
    db.commit()