from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    phone_number = Column(
        String,
        nullable=True
    )

    city = Column(
        String,
        nullable=True
    )

    bio = Column(
        String,
        nullable=True
    )

    password = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    activities = relationship(
        "Activity",
        back_populates="creator"
    )

    participation_requests = relationship(
        "Participation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

