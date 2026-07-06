from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_dependency import get_current_user
from app.db.dependencies import get_db
from app.models.user import User

from typing import List

from app.models.activity import Activity
from app.schemas.participation import ParticipationResponse
from app.schemas.activity import ActivityResponse
from app.schemas.user import UserResponse
from app.schemas.user import UserUpdate
from app.models.participation import Participation

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def get_my_profile(
        current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "city": current_user.city,
        "bio": current_user.bio
    }

@router.put(
    "/me",
    response_model=UserResponse
)
def update_my_profile(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    current_user.name = user_update.name
    current_user.phone_number = user_update.phone_number
    current_user.city = user_update.city
    current_user.bio = user_update.bio

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get(
    "/me/activities/created",
    response_model=List[ActivityResponse]
)
def get_created_activities(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activities = (
        db.query(Activity)
        .filter(
            Activity.created_by == current_user.id
        )
        .all()
    )

    return activities


@router.get(
    "/me/activities/joined",
    response_model=List[ActivityResponse]
)
def get_joined_activities(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activities = (
        db.query(Activity)
        .join(
            Participation,
            Activity.id == Participation.activity_id
        )
        .filter(
            Participation.user_id == current_user.id,
            Participation.status == "APPROVED"
        )
        .all()
    )

    return activities


@router.get(
    "/me/participation/pending",
    response_model=List[ParticipationResponse]
)
def get_pending_requests(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    requests = (
        db.query(Participation)
        .filter(
            Participation.user_id == current_user.id,
            Participation.status == "PENDING"
        )
        .all()
    )

    return requests
