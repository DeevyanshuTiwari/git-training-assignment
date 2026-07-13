from datetime import date, time, datetime
from pydantic import BaseModel, Field, field_validator


class ActivityCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str

    activity_date: date
    activity_time: time

    max_participants: int = Field(gt=0)

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Title must have at least 3 characters")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if len(v.strip().split()) < 3:
            raise ValueError("Description must have at least 3 words")
        return v


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

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Title must have at least 3 characters")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v:
            if len(v.strip().split()) < 3:
                raise ValueError("Description must have at least 3 words")
        return v


class ActivityResponse(BaseModel):
    id: int

    title: str
    description: str
    category: str
    location: str

    activity_date: date
    activity_time: time

    max_participants: int
    participants_count: int | None = 0
    status: str
    created_by: int
    organizer_name: str | None = None

    created_at: datetime

    class Config:
        from_attributes = True
