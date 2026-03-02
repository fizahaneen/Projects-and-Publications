# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, SessionLocal, Base
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Industry Connect Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/partners/", response_model=schemas.IndustryPartnerOut)
def add_partner(partner: schemas.IndustryPartnerCreate, db: Session = Depends(get_db)):
    return crud.create_partner(db, partner)

@app.get("/partners/", response_model=list[schemas.IndustryPartnerOut])
def read_partners(db: Session = Depends(get_db)):
    return crud.get_partners(db)

@app.get("/partners/{partner_id}", response_model=schemas.IndustryPartnerOut)
def read_partner(partner_id: int, db: Session = Depends(get_db)):
    partner = crud.get_partner(db, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@app.put("/partners/{partner_id}", response_model=schemas.IndustryPartnerOut)
def update_partner(partner_id: int, partner_update: schemas.IndustryPartnerUpdate, db: Session = Depends(get_db)):
    updated = crud.update_partner(db, partner_id, partner_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Partner not found")
    return updated

@app.delete("/partners/{partner_id}")
def delete_partner(partner_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_partner(db, partner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Partner not found")
    return {"message": "Partner deleted"}

@app.post("/link/", response_model=schemas.UserIndustryLinkOut)
def link_user(link: schemas.UserIndustryLinkCreate, db: Session = Depends(get_db)):
    return crud.link_user_to_partner(db, link)

@app.get("/links/", response_model=list[schemas.UserIndustryLinkOut])
def get_links(db: Session = Depends(get_db)):
    return crud.get_user_links(db)

@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=list[schemas.Event])
def get_upcoming_events(db: Session = Depends(get_db)):
    return db.query(models.Event).filter(models.Event.datetime > datetime.now()).all()

@app.get("/events/{event_id}", response_model=schemas.Event)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/events/register/")
def register_user(reg: schemas.RegisterUser, db: Session = Depends(get_db)):
    db_reg = models.EventRegistration(event_id=reg.event_id, user_id=reg.user_id)
    db.add(db_reg)
    db.commit()
    return {"msg": "User registered successfully"}

@app.get("/events/{event_id}/registrations/")
def get_registrations(event_id: int, db: Session = Depends(get_db)):
    registrations = db.query(models.EventRegistration).filter(models.EventRegistration.event_id == event_id).all()
    return registrations

@app.post("/events/feedback/")
def submit_feedback(fb: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    feedback = models.EventFeedback(**fb.dict())
    db.add(feedback)
    db.commit()
    return {"msg": "Feedback submitted"}


