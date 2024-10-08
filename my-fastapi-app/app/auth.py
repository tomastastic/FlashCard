from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException 
from pydantic import BaseModel 
from sqlalchemy.orm import Session 
from starlette import status 
from dotenv import load_dotenv
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os

from db import get_db
from models import User 
from schemas import UserBase, FlashcardType, FlashcardBase, CreateUserRequest, Token
#from router import auth_router, main_router

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Load environment variables from .env file
load_dotenv()
# Access the environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # bcrypt hashing algorithm
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # OAuth2 password bearer


'''
db_dependency = Annotated[Session, Depends(get_db)]                       
#user_dependency = Annotated [dict, Depends (get_current_user)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    existing_user = db.query(User).filter(
        (User.username == create_user_request.username) | (User.email == create_user_request.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists."
        )
    create_user_model = User(
        username=create_user_request.username,
        password=bcrypt_context.hash(create_user_request.password),
        email=create_user_request.email,
        created_at=datetime.now(),
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )
    access_token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": access_token, "token_type": "bearer"}
'''
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user



def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated [str, Depends (oauth2_bearer)]):
    try:
        payload = jwt.decode (token, SECRET_KEY, algorithms=[ALGORITHM] )
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


## functions for creating user and token
async def create_user(db: get_db, create_user_request: CreateUserRequest):
    existing_user = db.query(User).filter(
        (User.username == create_user_request.username) | (User.email == create_user_request.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists."
        )
    create_user_model = User(
        username=create_user_request.username,
        password=bcrypt_context.hash(create_user_request.password),
        email=create_user_request.email,
        created_at=datetime.now(),
    )
    db.add(create_user_model)
    db.commit()
    return {"message": "User created successfully"}

async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: get_db):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )
    access_token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": access_token, "token_type": "bearer"}