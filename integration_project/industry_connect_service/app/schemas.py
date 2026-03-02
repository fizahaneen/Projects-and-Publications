# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class IndustryPartnerBase(BaseModel):
    company_name: str
    domain: str
    contact_person: str
    contact_email: EmailStr
    description: Optional[str] = None

class IndustryPartnerCreate(IndustryPartnerBase):
    pass

class IndustryPartnerUpdate(BaseModel):
    company_name: Optional[str]
    domain: Optional[str]
    contact_person: Optional[str]
    contact_email: Optional[EmailStr]
    description: Optional[str]

class IndustryPartnerOut(IndustryPartnerBase):
    id: int

    class Config:
        orm_mode = True

class UserIndustryLinkCreate(BaseModel):
    user_id: int
    partner_id: int

class UserIndustryLinkOut(UserIndustryLinkCreate):
    id: int

    class Config:
        orm_mode = True

from pydantic import BaseModel
from datetime import datetime

class EventBase(BaseModel):
    title: str
    description: str
    datetime: datetime
    mode: str  # "online"/"offline"
    location: str
    host_organization: str
    max_participants: int

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    class Config:
        orm_mode = True

class RegisterUser(BaseModel):
    event_id: int
    user_id: int

class FeedbackCreate(BaseModel):
    event_id: int
    user_id: int
    feedback: str
