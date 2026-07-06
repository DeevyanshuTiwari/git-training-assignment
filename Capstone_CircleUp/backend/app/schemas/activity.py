from datetime import date, time, datetime
from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str

    activity_date: date
    activity_time: time

    max_participants: int = Field(gt=0)


class ActivityUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    location: str | None = None

    activity_date: date | None = None
    activity_time: time | None = None

    max_participants: int | None = Field(
        default=None,
        gt=0
    )


class ActivityResponse(BaseModel):
    id: int

    title: str
    description: str
    category: str
    location: str

    activity_date: date
    activity_time: time

    max_participants: int

    status: str

    created_by: int

    created_at: datetime

    class Config:
        from_attributes = True
