from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.dependencies import get_db
from app.core.auth_dependency import get_current_user
from app.models.user import User
from app.schemas.participation import ParticipationResponse
from app.services import participation_service

router = APIRouter(prefix="/participation", tags=["Participation"])


@router.post("/activities/{activity_id}/request", response_model=ParticipationResponse, status_code=201)
def request_participation(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return participation_service.request_participation(db, current_user, activity_id)


@router.get("/activities/{activity_id}/requests", response_model=List[ParticipationResponse])
def get_activity_requests(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return participation_service.get_activity_requests(db, current_user, activity_id)


@router.put("/requests/{request_id}/approve", response_model=ParticipationResponse)
def approve_request(
        request_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return participation_service.approve_request(db, current_user, request_id)


@router.put("/requests/{request_id}/reject", response_model=ParticipationResponse)
def reject_request(
        request_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return participation_service.reject_request(db, current_user, request_id)


@router.delete("/requests/{request_id}", status_code=204)
def withdraw_request(
        request_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    participation_service.withdraw_request(db, current_user, request_id)
    return None


@router.delete("/activities/{activity_id}/leave", status_code=204)
def leave_activity(
        activity_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    participation_service.leave_activity(db, current_user, activity_id)
    return None
