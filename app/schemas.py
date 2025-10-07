from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime


# -----------------------------
# User Schemas
# -----------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# -----------------------------
# Token Schema
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# Website Schemas
# -----------------------------
class WebsiteBase(BaseModel):
    name: str
    domain: str


class WebsiteCreate(WebsiteBase):
    pass


class WebsiteResponse(BaseModel):
    id: int
    name: str
    domain: str
    verification_token: str
    is_verified: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# -----------------------------
# Ad Event Schemas
# -----------------------------
class AdEventBase(BaseModel):
    event_type: str  # "click" or "impression"
    website_id: int


class AdEventResponse(BaseModel):
    id: int
    event_type: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# -----------------------------
# Dashboard Stats Schema
# -----------------------------
class WebsiteStats(BaseModel):
    website_id: int
    name: str
    domain: str
    impressions: int
    clicks: int
    estimated_revenue: float


# -----------------------------
# Verification Schema
# -----------------------------
class VerificationCheck(BaseModel):
    domain: str
    verification_token: str
    verified: bool
