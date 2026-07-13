from sqlalchemy.orm import Session
from app.models.user import User
from app.models.activity import Activity
from app.models.participation import Participation
from app.enums.participation_status import ParticipationStatus
from app.schemas.user import UserUpdate
from app.repositories import user_repo


def update_profile(db: Session, current_user: User, user_update: UserUpdate):
    current_user.name = user_update.name
    current_user.phone_number = user_update.phone_number
    current_user.city = user_update.city
    current_user.bio = user_update.bio
    return user_repo.update_user(db, current_user)


def get_created_activities(db: Session, current_user: User):
    return db.query(Activity).filter(Activity.created_by == current_user.id).all()


def get_joined_activities(db: Session, current_user: User):
    return (
        db.query(Activity)
        .join(Participation, Activity.id == Participation.activity_id)
        .filter(
            Participation.user_id == current_user.id,
            Participation.status == ParticipationStatus.APPROVED
        )
        .all()
    )


def get_pending_requests(db: Session, current_user: User):
    requests = (
        db.query(Participation, Activity.title.label("activity_title"))
        .join(Activity, Participation.activity_id == Activity.id)
        .filter(
            Participation.user_id == current_user.id,
            Participation.status == ParticipationStatus.PENDING
        )
        .all()
    )

    return [
        {
            "id": r.Participation.id,
            "activity_id": r.Participation.activity_id,
            "user_id": r.Participation.user_id,
            "status": r.Participation.status.value if hasattr(r.Participation.status,
                                                              'value') else r.Participation.status,
            "activity_title": r.activity_title
        }
        for r in requests
    ]


def get_rejected_requests(db: Session, current_user: User):
    requests = (
        db.query(Participation, Activity.title.label("activity_title"))
        .join(Activity, Participation.activity_id == Activity.id)
        .filter(
            Participation.user_id == current_user.id,
            Participation.status == ParticipationStatus.REJECTED
        )
        .all()
    )

    return [
        {
            "id": r.Participation.id,
            "activity_id": r.Participation.activity_id,
            "user_id": r.Participation.user_id,
            "status": r.Participation.status.value if hasattr(r.Participation.status,
                                                              'value') else r.Participation.status,
            "activity_title": r.activity_title
        }
        for r in requests
    ]
