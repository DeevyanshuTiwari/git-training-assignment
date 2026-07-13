from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.participation import Participation
from app.enums.participation_status import ParticipationStatus
from app.enums.activity_status import ActivityStatus
from app.repositories import activity_repo, participation_repo


def request_participation(db: Session, current_user: User, activity_id: int):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
    if activity.created_by == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot join your own activity.")

    existing_request = participation_repo.get_user_participation(db, current_user.id, activity_id)
    if existing_request:
        raise HTTPException(status_code=400, detail="Participation request already exists.")

    if activity.status == ActivityStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cancelled activities cannot accept requests.")
    if activity.status == ActivityStatus.FULL:
        raise HTTPException(status_code=400, detail="Activity is already full.")

    participation = Participation(
        activity_id=activity.id,
        user_id=current_user.id,
        status=ParticipationStatus.PENDING
    )
    return participation_repo.create_request(db, participation)


def get_activity_requests(db: Session, current_user: User, activity_id: int):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
    if activity.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to view these requests.")

    requests = db.query(Participation, User.name.label("user_name")) \
        .join(User, Participation.user_id == User.id) \
        .filter(Participation.activity_id == activity_id) \
        .all()

    return [
        {
            "id": r.Participation.id,
            "activity_id": r.Participation.activity_id,
            "user_id": r.Participation.user_id,
            "status": r.Participation.status.value if hasattr(r.Participation.status,
                                                              'value') else r.Participation.status,
            "user_name": r.user_name
        }
        for r in requests
    ]


def approve_request(db: Session, current_user: User, request_id: int):
    participation = participation_repo.get_request_by_id(db, request_id)
    if not participation:
        raise HTTPException(status_code=404, detail="Participation request not found.")

    activity = activity_repo.get_activity_by_id(db, participation.activity_id)
    if activity.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to approve requests.")

    if participation.status == ParticipationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Request already approved.")

    approved_count = participation_repo.get_approved_count(db, activity.id)
    if approved_count >= activity.max_participants:
        raise HTTPException(status_code=400, detail="Activity is already full.")

    participation = participation_repo.update_status(db, participation, ParticipationStatus.APPROVED)

    # Check if full after approval
    approved_count += 1
    if approved_count >= activity.max_participants:
        activity.status = ActivityStatus.FULL
        activity_repo.update_activity(db, activity)

    return participation


def reject_request(db: Session, current_user: User, request_id: int):
    participation = participation_repo.get_request_by_id(db, request_id)
    if not participation:
        raise HTTPException(status_code=404, detail="Participation request not found.")

    activity = activity_repo.get_activity_by_id(db, participation.activity_id)
    if activity.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to reject requests.")

    if participation.status == ParticipationStatus.REJECTED:
        raise HTTPException(status_code=400, detail="Request already rejected.")

    return participation_repo.update_status(db, participation, ParticipationStatus.REJECTED)


def withdraw_request(db: Session, current_user: User, request_id: int):
    participation = participation_repo.get_request_by_id(db, request_id)
    if not participation:
        raise HTTPException(status_code=404, detail="Participation request not found.")
    if participation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only withdraw your own requests.")

    participation_repo.delete_request(db, participation)


def leave_activity(db: Session, current_user: User, activity_id: int):
    participation = participation_repo.get_user_participation(db, current_user.id, activity_id)
    if not participation or participation.status != ParticipationStatus.APPROVED:
        raise HTTPException(status_code=404, detail="Participation record not found or not approved.")

    activity = activity_repo.get_activity_by_id(db, activity_id)
    participation_repo.delete_request(db, participation)

    if activity and activity.status == ActivityStatus.FULL:
        approved_count = participation_repo.get_approved_count(db, activity.id)
        if approved_count < activity.max_participants:
            activity.status = ActivityStatus.OPEN
            activity_repo.update_activity(db, activity)
