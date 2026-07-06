from datetime import datetime

from pydantic import BaseModel, EmailStr


class ParticipationCreate(BaseModel):
    pass


class ParticipationResponse(BaseModel):
    id: int
    activity_id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str | None = None
    city: str | None = None
    bio: str | None = None

    class Config:
        from_attributes = True


class ParticipationUpdate(BaseModel):
    status: str
