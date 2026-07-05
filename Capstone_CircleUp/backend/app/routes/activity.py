from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.auth_dependency import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.schemas.participation import ParticipantResponse
from app.services import activity_service

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(
        activity: ActivityCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return activity_service.create_activity(db, current_user, activity)


@router.get("", response_model=list[ActivityResponse])
def get_all_activities(
        title: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        activity_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    return activity_service.get_all_activities(db, title, category, location, activity_date)


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    return activity_service.get_activity_by_id(db, activity_id)


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
        activity_id: int,
        activity_update: ActivityUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return activity_service.update_activity(db, current_user, activity_id, activity_update)


@router.put("/{activity_id}/cancel", response_model=ActivityResponse)
def cancel_activity(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return activity_service.cancel_activity(db, current_user, activity_id)


@router.get("/{activity_id}/organizer-contact")
def get_organizer_contact(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return activity_service.get_organizer_contact(db, current_user, activity_id)


@router.get("/{activity_id}/participants", response_model=List[ParticipantResponse])
def get_approved_participants(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return activity_service.get_approved_participants(db, current_user, activity_id)
