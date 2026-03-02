# integration_service.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
import httpx
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROCESS_SERVICE_URL = os.getenv("PROCESS_SERVICE_URL", "http://localhost:8000")
INDUSTRY_SERVICE_URL = os.getenv("INDUSTRY_SERVICE_URL", "http://localhost:8001")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./integration.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class ProcessPartnerLink(Base):
    __tablename__ = "process_partner_links"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, nullable=False)
    partner_id = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

# Schema
class ProcessPartnerLinkCreate(BaseModel):
    process_id: int
    partner_id: int

class ProcessPartnerLinkResponse(BaseModel):
    id: int
    process_id: int
    partner_id: int

    class Config:
        orm_mode = True

class ProcessResponse(BaseModel):
    id: int
    name: str
    amount: int
    completed_qty: int

class PartnerResponse(BaseModel):
    id: int
    company_name: str
    domain: str
    contact_person: str
    contact_email: str
    description: Optional[str] = None

# API Client for Process Service
async def get_processes():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PROCESS_SERVICE_URL}/processes/")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch processes")
        return response.json()

async def get_process(process_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PROCESS_SERVICE_URL}/processes/{process_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch process")
        return response.json()

# API Client for Industry Service
async def get_partners():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INDUSTRY_SERVICE_URL}/partners/")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch partners")
        return response.json()

async def get_partner(partner_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INDUSTRY_SERVICE_URL}/partners/{partner_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch partner")
        return response.json()

# FastAPI app
app = FastAPI(title="Process-Industry Integration Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/processes/", response_model=List[ProcessResponse])
async def read_processes():
    """Fetch all processes from the Process Definition service"""
    return await get_processes()

@app.get("/partners/", response_model=List[PartnerResponse])
async def read_partners():
    """Fetch all industry partners from the Industry Connect service"""
    return await get_partners()

@app.post("/link/", response_model=ProcessPartnerLinkResponse)
async def link_process_to_partner(link_data: ProcessPartnerLinkCreate, db: Session = Depends(get_db)):
    """Create a link between a process and an industry partner"""
    process_id = link_data.process_id
    partner_id = link_data.partner_id
    
    # For debugging
    print(f"Attempting to link process {process_id} with partner {partner_id}")
    
    # Verify process exists
    process_url = f"{PROCESS_SERVICE_URL}/processes/{process_id}"
    print(f"Verifying process at: {process_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            process_response = await client.get(process_url)
            print(f"Process service response: {process_response.status_code}")
            if process_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Process not found")
    except Exception as e:
        print(f"Error verifying process: {str(e)}")
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Verify partner exists
    try:
        partner = await get_partner(partner_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Create the link
    link = ProcessPartnerLink(process_id=process_id, partner_id=partner_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link    

@app.get("/partner/{partner_id}/processes", response_model=List[ProcessResponse])
async def get_partner_processes(partner_id: int, db: Session = Depends(get_db)):
    """Get all processes linked to a specific industry partner"""
    # Check if partner exists
    try:
        partner = await get_partner(partner_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Get all processes linked to this partner
    links = db.query(ProcessPartnerLink).filter(ProcessPartnerLink.partner_id == partner_id).all()
    
    if not links:
        return []
    
    # Get process details for each linked process
    processes = []
    for link in links:
        try:
            process = await get_process(link.process_id)
            processes.append(process)
        except HTTPException:
            continue  # Skip if process no longer exists
    
    return processes

@app.get("/process/{process_id}/partners", response_model=List[PartnerResponse])
async def get_process_partners(process_id: int, db: Session = Depends(get_db)):
    """Get all industry partners linked to a specific process"""
    # Check if process exists
    try:
        process = await get_process(process_id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Get all partners linked to this process
    links = db.query(ProcessPartnerLink).filter(ProcessPartnerLink.process_id == process_id).all()
    
    if not links:
        return []
    
    # Get partner details for each linked partner
    partners = []
    for link in links:
        try:
            partner = await get_partner(link.partner_id)
            partners.append(partner)
        except HTTPException:
            continue  # Skip if partner no longer exists
    
    return partners

@app.delete("/link/")
async def unlink_process_from_partner(process_id: int, partner_id: int, db: Session = Depends(get_db)):
    """Remove link between a process and an industry partner"""
    link = db.query(ProcessPartnerLink).filter(
        ProcessPartnerLink.process_id == process_id,
        ProcessPartnerLink.partner_id == partner_id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
    return {"message": "Link removed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)