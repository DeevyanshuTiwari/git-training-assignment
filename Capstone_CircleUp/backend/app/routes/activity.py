from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_dependency import get_current_user
from app.db.dependencies import get_db
from app.models.participation import Participation

from app.models.user import User
from app.models.activity import Activity

from typing import List
from datetime import date
from typing import Optional

from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse
)
from app.schemas.participation import ParticipantResponse

router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=201
)
def create_activity(
        activity: ActivityCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activity_datetime = datetime.combine(
        activity.activity_date,
        activity.activity_time
    )

    if activity_datetime <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Activity must be scheduled in the future."
        )

    new_activity = Activity(
        title=activity.title,
        description=activity.description,
        category=activity.category,
        location=activity.location,
        activity_date=activity.activity_date,
        activity_time=activity.activity_time,
        max_participants=activity.max_participants,
        status="OPEN",
        created_by=current_user.id
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity



@router.get(
    "",
    response_model=list[ActivityResponse]
)
def get_all_activities(
        title: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        activity_date: Optional[date] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Activity).filter(
        Activity.status == "OPEN"
    )

    if title:
        query = query.filter(
            Activity.title.ilike(f"%{title}%")
        )

    if category:
        query = query.filter(
            Activity.category == category
        )

    if location:
        query = query.filter(
            Activity.location.ilike(f"%{location}%")
        )

    if activity_date:
        query = query.filter(
            Activity.activity_date == activity_date
        )

    query = query.order_by(
        Activity.activity_date.asc(),
        Activity.activity_time.asc()
    )

    return query.all()


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse
)
def get_activity(
        activity_id: int,
        db: Session = Depends(get_db)
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    return activity


@router.put(
    "/{activity_id}",
    response_model=ActivityResponse
)
def update_activity(
        activity_id: int,
        activity_update: ActivityUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    if activity.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own activities."
        )

    if (
            activity_update.activity_date
            and activity_update.activity_time
    ):

        updated_datetime = datetime.combine(
            activity_update.activity_date,
            activity_update.activity_time
        )

        if updated_datetime <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Activity must be scheduled in the future."
            )

    update_data = activity_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)

    return activity


@router.put(
    "/{activity_id}/cancel",
    response_model=ActivityResponse
)
def cancel_activity(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found"
        )

    if activity.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own activities."
        )

    if activity.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Activity is already cancelled."
        )

    activity.status = "CANCELLED"

    db.commit()
    db.refresh(activity)

    return activity


@router.get("/{activity_id}/organizer-contact")
def get_organizer_contact(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found."
        )

    participation = (
        db.query(Participation)
        .filter(
            Participation.activity_id == activity_id,
            Participation.user_id == current_user.id,
            Participation.status == "APPROVED"
        )
        .first()
    )

    if participation is None:
        raise HTTPException(
            status_code=403,
            detail="Contact information is available only after approval."
        )

    organizer = (
        db.query(User)
        .filter(User.id == activity.created_by)
        .first()
    )

    return {
        "name": organizer.name,
        "phone_number": organizer.phone_number
    }


@router.get("/{activity_id}/participants", response_model=List[ParticipantResponse])
def get_approved_participants(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    activity = (
        db.query(Activity)
        .filter(Activity.id == activity_id)
        .first()
    )

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found."
        )

    if activity.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the organizer can view participants."
        )

    participants = (
        db.query(User)
        .join(
            Participation,
            User.id == Participation.user_id
        )
        .filter(
            Participation.activity_id == activity_id,
            Participation.status == "APPROVED"
        )
        .all()
    )

    return [
        {
            "id": participant.id,
            "name": participant.name,
            "email": participant.email,
            "phone_number": participant.phone_number,
            "city": participant.city,
            "bio": participant.bio
        }
        for participant in participants
    ]
