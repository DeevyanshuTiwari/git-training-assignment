from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    location = Column(
        String,
        nullable=False
    )

    activity_date = Column(
        Date,
        nullable=False
    )

    activity_time = Column(
        Time,
        nullable=False
    )

    max_participants = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        default="OPEN"
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    creator = relationship(
        "User",
        back_populates="activities"
    )

    participation_requests = relationship(
        "Participation",
        back_populates="activity",
        cascade="all, delete-orphan"
    )
