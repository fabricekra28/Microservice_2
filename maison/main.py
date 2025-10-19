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

class Maison(Base):
    __tablename__ = "maisons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Maison Service App2")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MaisonCreate(BaseModel):
    name: str
    address: str = None

class MaisonResponse(BaseModel):
    id: int
    name: str
    address: str = None

    class Config:
        orm_mode = True

@app.get("/maisons", response_model=list[MaisonResponse])
def list_maisons(db: Session = Depends(get_db)):
    return db.query(Maison).all()

@app.post("/maisons", response_model=MaisonResponse)
def create_maison(maison: MaisonCreate, db: Session = Depends(get_db)):
    db_maison = Maison(name=maison.name, address=maison.address)
    db.add(db_maison)
    db.commit()
    db.refresh(db_maison)
    return db_maison

@app.get("/maisons/{maison_id}", response_model=MaisonResponse)
def get_maison(maison_id: int, db: Session = Depends(get_db)):
    maison = db.get(Maison, maison_id)
    if not maison:
        raise HTTPException(status_code=404, detail="Maison not found")
    return maison

@app.put("/maisons/{maison_id}", response_model=MaisonResponse)
def update_maison(maison_id: int, maison: MaisonCreate, db: Session = Depends(get_db)):
    db_maison = db.get(Maison, maison_id)
    if not db_maison:
        raise HTTPException(status_code=404, detail="Maison not found")
    db_maison.name = maison.name
    db_maison.address = maison.address
    db.commit()
    db.refresh(db_maison)
    return db_maison

@app.delete("/maisons/{maison_id}")
def delete_maison(maison_id: int, db: Session = Depends(get_db)):
    db_maison = db.get(Maison, maison_id)
    if not db_maison:
        raise HTTPException(status_code=404, detail="Maison not found")
    db.delete(db_maison)
    db.commit()
    return {"message": "Maison deleted successfully"}
