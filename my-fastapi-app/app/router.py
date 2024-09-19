# FILE: router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Annotated
from sqlalchemy.orm import Session
from auth import get_current_user, create_user, login_for_access_token, authenticate_user, create_access_token
from schemas import FlashcardBase, UserBase, CreateUserRequest, Token, CardSchedule #FlashcardRating
from db import get_db
import models as models

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

### Cardschedule endpoint: 
'''first check if the user has a flashcard in their CardSchedule and if it doesnt, 
add the first flashcard from the flashcard table (order based on the flashcard id). 
if the user does have a flashcard in their Cardschedule then add the subsequent flashcard (order based on the flashcard id)'''

from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound

@main_router.post("/cardschedule/add_flashcard", response_model=CardSchedule)
def add_flashcard_to_schedule(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Check if the user has any flashcards in their CardSchedule
    try:
        last_flashcard = db.query(models.CardSchedule).filter(models.CardSchedule.user_id == current_user['id']).order_by(models.CardSchedule.flashcard_id.desc()).first()
    except NoResultFound:
        last_flashcard = None

    # If the user has no flashcards in their CardSchedule, add the first flashcard from the Flashcard table
    if last_flashcard is None:
        flashcard_to_add = db.query(models.Flashcard).order_by(models.Flashcard.id).first()
    # If the user has flashcards in their CardSchedule, add the subsequent flashcard
    else:
        flashcard_to_add = db.query(models.Flashcard).filter(models.Flashcard.id > last_flashcard.flashcard_id).order_by(models.Flashcard.id).first()

    if flashcard_to_add is None:
        raise HTTPException(status_code=400, detail="No more flashcards to add")

    # Add the flashcard to the user's CardSchedule
    new_schedule = models.CardSchedule(
        flashcard_id=flashcard_to_add.id,
        user_id=current_user['id'],
        stability=0.0,
        difficulty=0.0,
        elapsed_days=0,
        scheduled_days=0,
        reps=0,
        lapses=0,
        state='new'
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

## Cardschedule enpoint:
''' 
This endpoint will first check if the user has any flashcards in their CardSchedule. 
If they don't, it will add the first flashcard from the Flashcard table. 
If they do, it will add the subsequent flashcard.
'''
from fastapi import HTTPException
from sqlalchemy import func
from typing import List

from sqlalchemy import func, extract
@main_router.get("/cardschedule/due_flashcards", response_model=List[FlashcardBase])
def get_due_flashcards(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    current_time = func.now()
    due_flashcards = db.query(models.CardSchedule, models.Flashcard).join(models.Flashcard, models.CardSchedule.flashcard_id == models.Flashcard.id).filter(models.CardSchedule.user_id == current_user['id'], models.CardSchedule.due <= current_time).all()

    if not due_flashcards:
        raise HTTPException(status_code=404, detail="No flashcards due")

    return [flashcard for _, flashcard in due_flashcards]
## Cardschedule endpoint:
'''
Make an endpoint called “scheduleUpdate” that takes as input one or more flashcard ids. 
Then it will add 5 minutes to the due date of the flashcard on the cardschedule for the user
'''
from datetime import timedelta

@main_router.put("/scheduleUpdate/")
def update_schedule(flashcard_ids: List[int], db: Session = Depends(get_db)):
    for flashcard_id in flashcard_ids:
        db_cardschedule = db.query(models.CardSchedule).filter(models.CardSchedule.flashcard_id == flashcard_id).first()
        if not db_cardschedule:
            raise HTTPException(status_code=404, detail=f"CardSchedule for flashcard_id {flashcard_id} not found")
        db_cardschedule.due += timedelta(days=1)
    db.commit()
    return {"message": "Schedule updated successfully"}


## FSRS schedule endpoint
'''
modified update_schedule endpoint that incorporates the FSRS algorithm
'''
'''
from fsrs import FSRS, Card, Rating
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

@main_router.put("/FSRS_schedule")
async def update_flashcard_schedules(ratings: List[FlashcardRating], db: Session = Depends(get_db)):
    """
    Updates flashcard schedules based on user ratings using the FSRS algorithm.
    Args:
        ratings: A list of FlashcardRating objects containing flashcard_id and rating.
        db: Database session.
    Returns:
        A message indicating successful schedule updates.
    """
    for rating in ratings:
        card_schedule = db.query(models.CardSchedule).filter_by(flashcard_id=rating.flashcard_id).first()
        if not card_schedule:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        # Create FSRS Card object from database data
        card = Card(
            due=card_schedule.due.replace(tzinfo=ZoneInfo("UTC")) if card_schedule.due.tzinfo is None else card_schedule.due,
            stability=card_schedule.stability,
            difficulty=card_schedule.difficulty,
            elapsed_days=card_schedule.elapsed_days,
            scheduled_days=card_schedule.scheduled_days,
            reps=card_schedule.reps,
            lapses=card_schedule.lapses,
            state=card_schedule.state,
        )
        # Apply FSRS Algorithm
        fsrs = FSRS()
        now = datetime.now(timezone.utc)
        scheduling_cards = fsrs.repeat(card, now)
        new_card = scheduling_cards[Rating(rating.rating)].card
        # Update database with new schedule
        card_schedule.due = new_card.due
        card_schedule.stability = new_card.stability
        card_schedule.difficulty = new_card.difficulty
        card_schedule.elapsed_days = new_card.elapsed_days
        card_schedule.scheduled_days = new_card.scheduled_days
        card_schedule.reps = new_card.reps
        card_schedule.lapses = new_card.lapses
        card_schedule.state = new_card.state.value
        card_schedule.last_review = datetime.now(timezone.utc)
        db.commit()
    return {"message": "Flashcard schedules updated successfully."}
    '''