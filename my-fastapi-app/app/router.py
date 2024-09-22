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

# Register endpoint
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, create_user_request: CreateUserRequest):
    return await create_user(db, create_user_request)

# Log in endpoint
@auth_router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return await login_for_access_token(form_data, db)



# Get all flashcards endpoint
@main_router.get("/flashcards", response_model=List[FlashcardBase])
def read_flashcards(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    flashcards = db.query(models.Flashcard).offset(skip).limit(limit).all()
    return flashcards

# Get all users endpoint
@main_router.get("/users", response_model=List[UserBase])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@main_router.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return {"User": user}

# Cardschedule endpoint: 
'''first check if the user has a flashcard in their CardSchedule,
if it doesnt, add the first flashcard from the flashcard table (order based on flashcard id). 
if the user does have a flashcard in their Cardschedule then add the subsequent flashcard '''

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



# Cardschedule enpoint
''' 
This endpoint will first check if the user has any flashcards due down to the minute in their CardSchedule. 
If they don't have any due, it will inform the client.
'''
from fastapi import HTTPException
from sqlalchemy import func
from typing import List

@main_router.get("/cardschedule/due_flashcards", response_model=List[FlashcardBase])
def get_due_flashcards(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    current_time = func.now()
    truncated_current_time = func.date_format(current_time, '%Y-%m-%d %H:%i:00')
    due_flashcards = db.query(models.CardSchedule, models.Flashcard).join(models.Flashcard, models.CardSchedule.flashcard_id == models.Flashcard.id).filter(models.CardSchedule.user_id == current_user['id'], func.date_format(models.CardSchedule.due, '%Y-%m-%d %H:%i:00') <= truncated_current_time).all()

    if not due_flashcards:
        raise HTTPException(status_code=404, detail="No flashcards due")

    return [flashcard for _, flashcard in due_flashcards]


# Cardschedule endpoint:
'''
Make an endpoint called “scheduleUpdate” that takes as input one or more flashcard ids. 
Then it will add 5 minutes to the due date of the flashcard on the cardschedule for the user
'''
from datetime import timedelta

@main_router.put("/scheduleUpdate/")
def update_schedule(flashcard_ids: List[int], db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    for flashcard_id in flashcard_ids:
        db_cardschedule = db.query(models.CardSchedule).filter(models.CardSchedule.flashcard_id == flashcard_id,models.CardSchedule.user_id == current_user['id']).first()
        if not db_cardschedule:
            raise HTTPException(status_code=404, detail=f"CardSchedule for flashcard_id {flashcard_id} not found")
        db_cardschedule.due += timedelta(minutes=5)
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




### NEW add card endpoint


from fsrs import FSRS, Card, State, ReviewLog
from datetime import datetime, timezone

@main_router.post("/cardschedule/new_add_flashcard", response_model=CardSchedule)
def new_add_flashcard_to_schedule(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
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

    # Create FSRS Card object from database data
    card = Card(
        due=new_schedule.due,
        stability=new_schedule.stability,
        difficulty=new_schedule.difficulty,
        elapsed_days=new_schedule.elapsed_days,
        scheduled_days=new_schedule.scheduled_days,
        reps=new_schedule.reps,
        lapses=new_schedule.lapses,
        state=new_schedule.state,
        last_review=new_schedule.last_review
    )

    # Convert Card object back to dictionary and update the database
    card_dict = card.to_dict()
    new_schedule.due = card_dict["due"]
    new_schedule.stability = card_dict["stability"]
    new_schedule.difficulty = card_dict["difficulty"]
    new_schedule.elapsed_days = card_dict["elapsed_days"]
    new_schedule.scheduled_days = card_dict["scheduled_days"]
    new_schedule.reps = card_dict["reps"]
    new_schedule.lapses = card_dict["lapses"]
    new_schedule.state = card_dict["state"]
    new_schedule.last_review = card_dict["last_review"]

    db.commit()
    db.refresh(new_schedule)

    return new_schedule






### FSRS schedule endpoint


from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timezone




from fsrs import FSRS, Card, Rating, State

from auth import get_current_user, create_user, login_for_access_token, authenticate_user, create_access_token
from schemas import FlashcardBase, UserBase, CreateUserRequest, Token, CardSchedule, FlashcardRating, FlashcardRatingList
from db import get_db



@main_router.put("/scheduleUpdateFSRS/")
def fsrs_update_schedule(
    rating: FlashcardRating,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    
    user_id = current_user['id']
    
    try:
        schedule = db.query(models.CardSchedule).filter(
            models.CardSchedule.user_id == user_id,
            models.CardSchedule.flashcard_id == rating.flashcard_id
        ).first()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No matching flashcard schedule found for flashcard ID {rating.flashcard_id}"
            )

        fsrs = FSRS()
        review_time = datetime.now(timezone.utc)

        card_data = {
            "due": schedule.due.isoformat(),
            "stability": schedule.stability,
            "difficulty": schedule.difficulty,
            "elapsed_days": schedule.elapsed_days,
            "scheduled_days": schedule.scheduled_days,
            "reps": schedule.reps,
            "lapses": schedule.lapses,
            "state": schedule.state,
            "last_review": schedule.last_review.isoformat() if schedule.last_review else None
        }

        card = Card.from_dict(card_data)
        if not isinstance(card, Card):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to instantiate Card object from fsrs library"
        )
        
        '''
        scheduling_cards = SchedulingCards(card, review_time)
        new_card = scheduling_cards[rating.rating].card
        review_log = scheduling_cards[rating.rating].review_log

        schedule.due = new_card.due
        schedule.stability = new_card.stability
        schedule.difficulty = new_card.difficulty
        schedule.elapsed_days = new_card.elapsed_days
        schedule.scheduled_days = new_card.scheduled_days
        schedule.reps = new_card.reps
        schedule.lapses = new_card.lapses
        schedule.state = new_card.state.name
        schedule.last_review = review_time

        db.commit()'''


        
        return {"message": f"Successfully rescheduled flashcard with ID: {rating.flashcard_id}"}

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No matching flashcard schedule found for flashcard ID {rating.flashcard_id}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating schedule: {str(e)}"
        )


# github attempt

from fsrs import Card
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

@main_router.get("/cardschedule/{flashcard_id}", response_model=CardSchedule)
async def get_cardschedule(flashcard_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    schedule = db.query(models.CardSchedule).filter_by(flashcard_id=flashcard_id, user_id=current_user['id']).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="CardSchedule not found")
    
    card = Card(
        due=schedule.due.replace(tzinfo=ZoneInfo("UTC")) if schedule.due.tzinfo is None else schedule.due,
        stability=schedule.stability,
        difficulty=schedule.difficulty,
        elapsed_days=schedule.elapsed_days,
        scheduled_days=schedule.scheduled_days,
        reps=schedule.reps,
        lapses=schedule.lapses,
        state=schedule.state,
        last_review=schedule.last_review.replace(tzinfo=ZoneInfo("UTC")) if schedule.last_review.tzinfo is None else schedule.last_review
    )
    # Construct the response with required fields
    response = {
        "id": schedule.id,
        "flashcard_id": schedule.flashcard_id,
        "user_id": schedule.user_id,
        "due": card.due,
        "stability": card.stability,
        "difficulty": card.difficulty,
        "elapsed_days": card.elapsed_days,
        "scheduled_days": card.scheduled_days,
        "reps": card.reps,
        "lapses": card.lapses,
        "state": card.state,
        "last_review": card.last_review
    }
    return response


@main_router.get("/cardschedule/{flashcard_id}", response_model=CardSchedule)
async def get_Card_in_schedule(flashcard_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    schedule = db.query(models.CardSchedule).filter_by(flashcard_id=flashcard_id, user_id=current_user['id']).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="CardSchedule not found")
    
    card = Card(
        due=schedule.due.replace(tzinfo=ZoneInfo("UTC")) if schedule.due.tzinfo is None else schedule.due,
        stability=schedule.stability,
        difficulty=schedule.difficulty,
        elapsed_days=schedule.elapsed_days,
        scheduled_days=schedule.scheduled_days,
        reps=schedule.reps,
        lapses=schedule.lapses,
        state=schedule.state,
        last_review=schedule.last_review.replace(tzinfo=ZoneInfo("UTC")) if schedule.last_review.tzinfo is None else schedule.last_review
    )
    
    # Update the schedule with the card data
    schedule.due = card.due
    schedule.stability = card.stability
    schedule.difficulty = card.difficulty
    schedule.elapsed_days = card.elapsed_days
    schedule.scheduled_days = card.scheduled_days
    schedule.reps = card.reps
    schedule.lapses = card.lapses
    schedule.state = card.state
    schedule.last_review = card.last_review
    
    # Commit the changes to the database
    db.commit()
    db.refresh(schedule)
    
    # Construct the response with required fields
    response = {
        "id": schedule.id,
        "flashcard_id": schedule.flashcard_id,
        "user_id": schedule.user_id,
        "due": schedule.due,
        "stability": schedule.stability,
        "difficulty": schedule.difficulty,
        "elapsed_days": schedule.elapsed_days,
        "scheduled_days": schedule.scheduled_days,
        "reps": schedule.reps,
        "lapses": schedule.lapses,
        "state": schedule.state,
        "last_review": schedule.last_review
    }
    return response




from datetime import datetime, timezone
from fsrs import FSRS, Card, Rating



@main_router.put("/easy_review/{flashcard_id}")
def easy_review(flashcard_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Get the CardSchedule for the given flashcard_id
    card_schedule = db.query(models.CardSchedule).filter(
        models.CardSchedule.flashcard_id == flashcard_id,
        models.CardSchedule.user_id == current_user['id']
    ).first()

    if not card_schedule:
        raise HTTPException(status_code=404, detail="Flashcard not found in user's schedule")
    # Instantiate the Card object from CardSchedule
    
    try:
        card = Card(
            due=card_schedule.due.replace(tzinfo=timezone.utc),
            stability=card_schedule.stability,
            difficulty=card_schedule.difficulty,
            elapsed_days=card_schedule.elapsed_days,
            scheduled_days=card_schedule.scheduled_days,
            reps=card_schedule.reps,
            lapses=card_schedule.lapses,
            state=card_schedule.state,
            last_review=card_schedule.last_review.replace(tzinfo=timezone.utc)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to instantiate Card object: {str(e)}")
    # Review the card with a rating of Easy
    fsrs = FSRS()
    #reviewed_card, ReviewLog = fsrs.review_card(card, Rating.Easy)
    
    #
    scheduling_cards = fsrs.repeat(card, datetime.now(timezone.utc))
    reviewed_card = scheduling_cards[Rating.Easy].card
    
    
    # Update the database with the reviewed card
    card_schedule.due = reviewed_card.due.replace(tzinfo=None)
    card_schedule.stability = reviewed_card.stability
    card_schedule.difficulty = reviewed_card.difficulty
    card_schedule.elapsed_days = reviewed_card.elapsed_days
    card_schedule.scheduled_days = reviewed_card.scheduled_days
    card_schedule.reps = reviewed_card.reps
    card_schedule.lapses = reviewed_card.lapses
    card_schedule.state = reviewed_card.state
    card_schedule.last_review = datetime.now()

    db.commit()
    db.refresh(card_schedule)

    return card_schedule