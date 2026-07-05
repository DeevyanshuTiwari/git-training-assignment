from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityUpdate
from app.enums.activity_status import ActivityStatus
from app.repositories import activity_repo, participation_repo, user_repo
from app.models.participation import Participation
from app.enums.participation_status import ParticipationStatus


def create_activity(db: Session, current_user: User, activity_data: ActivityCreate):
    activity_datetime = datetime.combine(activity_data.activity_date, activity_data.activity_time)
    if activity_datetime <= datetime.now():
        raise HTTPException(status_code=400, detail="Activity must be scheduled in the future.")

    new_activity = Activity(
        title=activity_data.title,
        description=activity_data.description,
        category=activity_data.category,
        location=activity_data.location,
        activity_date=activity_data.activity_date,
        activity_time=activity_data.activity_time,
        max_participants=activity_data.max_participants,
        status=ActivityStatus.OPEN,
        created_by=current_user.id
    )
    return activity_repo.create_activity(db, new_activity)


def get_all_activities(
        db: Session,
        title: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        activity_date: Optional[date] = None
):
    activities = activity_repo.get_all_open_activities(db, title, category, location, activity_date)
    results = []
    for activity in activities:
        act_dict = {col.name: getattr(activity, col.name) for col in activity.__table__.columns}
        act_dict["participants_count"] = participation_repo.get_approved_count(db, activity.id)
        results.append(act_dict)
    return results


def get_activity_by_id(db: Session, activity_id: int):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    organizer = user_repo.get_user_by_id(db, activity.created_by)
    activity_dict = {col.name: getattr(activity, col.name) for col in activity.__table__.columns}
    activity_dict["organizer_name"] = organizer.name if organizer else "Anonymous"
    activity_dict["participants_count"] = participation_repo.get_approved_count(db, activity_id)
    return activity_dict


def update_activity(db: Session, current_user: User, activity_id: int, activity_update: ActivityUpdate):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    if activity.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own activities.")

    if activity_update.activity_date and activity_update.activity_time:
        updated_datetime = datetime.combine(activity_update.activity_date, activity_update.activity_time)
        if updated_datetime <= datetime.now():
            raise HTTPException(status_code=400, detail="Activity must be scheduled in the future.")

    update_data = activity_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(activity, key, value)

    return activity_repo.update_activity(db, activity)


def cancel_activity(db: Session, current_user: User, activity_id: int):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    if activity.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own activities.")
    if activity.status == ActivityStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Activity is already cancelled.")

    activity.status = ActivityStatus.CANCELLED
    return activity_repo.update_activity(db, activity)


def get_organizer_contact(db: Session, current_user: User, activity_id: int):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")

    participation = db.query(Participation).filter(
        Participation.activity_id == activity_id,
        Participation.user_id == current_user.id,
        Participation.status == ParticipationStatus.APPROVED
    ).first()

    if not participation:
        raise HTTPException(status_code=403, detail="Contact information is available only after approval.")

    organizer = user_repo.get_user_by_id(db, activity.created_by)
    return {"name": organizer.name, "phone_number": organizer.phone_number}


def get_approved_participants(db: Session, current_user: User, activity_id: int):
    activity = activity_repo.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
    if activity.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the organizer can view participants.")

    participants = (
        db.query(User)
        .join(Participation, User.id == Participation.user_id)
        .filter(
            Participation.activity_id == activity_id,
            Participation.status == ParticipationStatus.APPROVED
        )
        .all()
    )

    return [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "phone_number": p.phone_number,
            "city": p.city,
            "bio": p.bio
        } for p in participants
    ]
