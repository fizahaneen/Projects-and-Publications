# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey,Text
from sqlalchemy.orm import relationship
from app.database import Base

class IndustryPartner(Base):
    __tablename__ = "industry_partners"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    description = Column(Text)

    users = relationship("UserIndustryLink", back_populates="partner")

class UserIndustryLink(Base):
    __tablename__ = "user_industry_links"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # can be linked to your user service
    partner_id = Column(Integer, ForeignKey("industry_partners.id"))

    partner = relationship("IndustryPartner", back_populates="users")


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    datetime = Column(DateTime)
    mode = Column(String)  # "online" or "offline"
    location = Column(String)  # link or physical location
    host_organization = Column(String)
    max_participants = Column(Integer)

    registrations = relationship("EventRegistration", back_populates="event")
    feedbacks = relationship("EventFeedback", back_populates="event")


class EventRegistration(Base):
    __tablename__ = 'event_registrations'
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer)
    
    event = relationship("Event", back_populates="registrations")


class EventFeedback(Base):
    __tablename__ = 'event_feedbacks'
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer)
    feedback = Column(String)

    event = relationship("Event", back_populates="feedbacks")
