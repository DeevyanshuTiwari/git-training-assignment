from sqlalchemy.orm import Session
from app.models.participation import Participation
from app.enums.participation_status import ParticipationStatus


def create_request(db: Session, participation: Participation):
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return participation


def get_request_by_id(db: Session, request_id: int):
    return db.query(Participation).filter(Participation.id == request_id).first()


def get_requests_for_activity(db: Session, activity_id: int):
    return db.query(Participation).filter(Participation.activity_id == activity_id).all()


def get_approved_count(db: Session, activity_id: int):
    return db.query(Participation).filter(
        Participation.activity_id == activity_id,
        Participation.status == ParticipationStatus.APPROVED
    ).count()


def get_user_participation(db: Session, user_id: int, activity_id: int):
    return db.query(Participation).filter(
        Participation.activity_id == activity_id,
        Participation.user_id == user_id
    ).first()


def update_status(db: Session, participation: Participation, status: ParticipationStatus):
    participation.status = status
    db.commit()
    db.refresh(participation)
    return participation


def delete_request(db: Session, participation: Participation):
    db.delete(participation)
    db.commit()
