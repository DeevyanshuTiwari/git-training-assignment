from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.db.database import Base


class Participation(Base):
    __tablename__ = "participation_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    activity_id = Column(
        Integer,
        ForeignKey("activities.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String,
        default="PENDING"
    )

    requested_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    activity = relationship(
        "Activity",
        back_populates="participation_requests"
    )

    user = relationship(
        "User",
        back_populates="participation_requests"
    )
