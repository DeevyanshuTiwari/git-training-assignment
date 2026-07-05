from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.enums.activity_status import ActivityStatus
from typing import Optional
from datetime import date


def create_activity(db: Session, activity: Activity):
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_activity_by_id(db: Session, activity_id: int):
    return db.query(Activity).filter(Activity.id == activity_id).first()


def get_all_open_activities(
        db: Session,
        title: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        activity_date: Optional[date] = None
):
    query = db.query(Activity).filter(Activity.status == ActivityStatus.OPEN)

    if title:
        query = query.filter(Activity.title.ilike(f"%{title}%"))
    if category:
        query = query.filter(Activity.category == category)
    if location:
        query = query.filter(Activity.location.ilike(f"%{location}%"))
    if activity_date:
        query = query.filter(Activity.activity_date == activity_date)

    return query.order_by(Activity.activity_date.asc(), Activity.activity_time.asc()).all()


def update_activity(db: Session, activity: Activity):
    db.commit()
    db.refresh(activity)
    return activity
