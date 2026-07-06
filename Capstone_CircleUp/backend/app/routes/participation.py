from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.core.auth_dependency import get_current_user

from typing import List

from app.models.user import User
from app.models.activity import Activity
from app.models.participation import Participation
from app.schemas.participation import ParticipationResponse

router = APIRouter(
    prefix="/participation",
    tags=["Participation"]
)


@router.post(
    "/activities/{activity_id}/request",
    response_model=ParticipationResponse,
    status_code=201
)
def request_participation(
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

    if activity.created_by == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot join your own activity."
        )

    existing_request = (
        db.query(Participation)
        .filter(
            Participation.activity_id == activity_id,
            Participation.user_id == current_user.id
        )
        .first()
    )

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Participation request already exists."
        )

    if activity.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Cancelled activities cannot accept requests."
        )

    if activity.status == "FULL":
        raise HTTPException(
            status_code=400,
            detail="Activity is already full."
        )

    participation = Participation(
        activity_id=activity.id,
        user_id=current_user.id,
        status="PENDING"
    )

    db.add(participation)
    db.commit()
    db.refresh(participation)

    return participation


@router.get(
    "/activities/{activity_id}/requests",
    response_model=List[ParticipationResponse]
)
def get_activity_requests(
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
            detail="You are not allowed to view these requests."
        )

    requests = (
        db.query(Participation)
        .filter(
            Participation.activity_id == activity_id
        )
        .all()
    )

    return requests


@router.put(
    "/requests/{request_id}/approve",
    response_model=ParticipationResponse
)
def approve_request(
        request_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    participation = (
        db.query(Participation)
        .filter(Participation.id == request_id)
        .first()
    )

    if participation is None:
        raise HTTPException(
            status_code=404,
            detail="Participation request not found."
        )

    activity = (
        db.query(Activity)
        .filter(Activity.id == participation.activity_id)
        .first()
    )

    if activity.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to approve requests."
        )

    if participation.status == "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Request already approved."
        )

    approved_count = (
        db.query(Participation)
        .filter(
            Participation.activity_id == activity.id,
            Participation.status == "APPROVED"
        )
        .count()
    )

    if approved_count >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is already full."
        )

    participation.status = "APPROVED"

    approved_count += 1

    if approved_count >= activity.max_participants:
        activity.status = "FULL"

    db.commit()

    db.refresh(participation)

    return participation


@router.put(
    "/requests/{request_id}/reject",
    response_model=ParticipationResponse
)
def reject_request(
        request_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    participation = (
        db.query(Participation)
        .filter(Participation.id == request_id)
        .first()
    )

    if participation is None:
        raise HTTPException(
            status_code=404,
            detail="Participation request not found."
        )

    activity = (
        db.query(Activity)
        .filter(Activity.id == participation.activity_id)
        .first()
    )

    if activity.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to reject requests."
        )

    if participation.status == "REJECTED":
        raise HTTPException(
            status_code=400,
            detail="Request already rejected."
        )

    participation.status = "REJECTED"

    db.commit()
    db.refresh(participation)

    return participation
