# app/crud.py

from sqlalchemy.orm import Session
from app import models, schemas

def create_partner(db: Session, partner: schemas.IndustryPartnerCreate):
    db_partner = models.IndustryPartner(**partner.dict())
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner

def get_partners(db: Session):
    return db.query(models.IndustryPartner).all()

def get_partner(db: Session, partner_id: int):
    return db.query(models.IndustryPartner).filter(models.IndustryPartner.id == partner_id).first()

def update_partner(db: Session, partner_id: int, update_data: schemas.IndustryPartnerUpdate):
    db_partner = get_partner(db, partner_id)
    if db_partner:
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(db_partner, key, value)
        db.commit()
        db.refresh(db_partner)
    return db_partner

def delete_partner(db: Session, partner_id: int):
    db_partner = get_partner(db, partner_id)
    if db_partner:
        db.delete(db_partner)
        db.commit()
    return db_partner

def link_user_to_partner(db: Session, link: schemas.UserIndustryLinkCreate):
    db_link = models.UserIndustryLink(**link.dict())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def get_user_links(db: Session):
    return db.query(models.UserIndustryLink).all()
