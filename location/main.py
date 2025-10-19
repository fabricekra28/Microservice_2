from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    maison_id = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Location Service App2")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LocationCreate(BaseModel):
    maison_id: int
    description: str = None

class LocationResponse(BaseModel):
    id: int
    maison_id: int
    description: str = None

    class Config:
        orm_mode = True

@app.get("/locations", response_model=list[LocationResponse])
def list_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()

@app.post("/locations", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    db_location = Location(maison_id=location.maison_id, description=location.description)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@app.get("/locations/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@app.put("/locations/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, location: LocationCreate, db: Session = Depends(get_db)):
    db_location = db.get(Location, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    db_location.maison_id = location.maison_id
    db_location.description = location.description
    db.commit()
    db.refresh(db_location)
    return db_location

@app.delete("/locations/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    db_location = db.get(Location, location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(db_location)
    db.commit()
    return {"message": "Location deleted successfully"}
