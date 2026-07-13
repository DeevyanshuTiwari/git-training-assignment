from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.auth_dependency import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.activity import ActivityResponse
from app.schemas.participation import ParticipationResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "city": current_user.city,
        "bio": current_user.bio
    }


@router.put("/me", response_model=UserResponse)
def update_my_profile(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return user_service.update_profile(db, current_user, user_update)


@router.get("/me/activities/created", response_model=List[ActivityResponse])
def get_created_activities(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return user_service.get_created_activities(db, current_user)


@router.get("/me/activities/joined", response_model=List[ActivityResponse])
def get_joined_activities(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return user_service.get_joined_activities(db, current_user)


@router.get("/me/participation/pending", response_model=List[ParticipationResponse])
def get_pending_requests(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return user_service.get_pending_requests(db, current_user)
