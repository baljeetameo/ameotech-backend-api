# backend/app/bookdiscoverysprint.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session, declarative_base

from .models import DiscoverySprintRequest
from .schemas import DiscoverySprintCreate

from app.database import get_db
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

Base = declarative_base()
router = APIRouter(prefix="/bookdiscoverysprint", tags=["bookdiscoverysprint"])


@router.post("")
def book_discovery_sprint(payload: DiscoverySprintCreate, db: Session = Depends(get_db)):
    record = DiscoverySprintRequest(**payload.dict())
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
    "message": "Discovery sprint request submitted successfully",
    "id": record.id
    }