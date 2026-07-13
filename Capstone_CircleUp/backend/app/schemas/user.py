import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if v:
            clean_v = re.sub(r"[\s-]", "", v)
            if not re.match(r"^\+?[1-9]\d{1,14}$", clean_v):
                raise ValueError("Invalid phone number format")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    city: str | None = None
    bio: str | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Name must have at least 3 characters")
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if v:
            clean_v = re.sub(r"[\s-]", "", v)
            if not re.match(r"^(?:\+91|91|0)?[6-9]\d{9}$", clean_v):
                raise ValueError("Invalid Indian phone number")
        return v

    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v):
        if v:
            words = v.strip().split()
            if len(words) < 3:
                raise ValueError("Bio must have at least 3 words")
        return v
