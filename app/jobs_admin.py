# backend/app/jobs_admin.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt, JWTError

from .auth import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session
from .models import Job
from app.database import get_db

router = APIRouter(prefix="/admin/jobs", tags=["jobs-admin"])

class Jobs(BaseModel):
  id: int
  title: str
  location: str
  type: str
  summary: str
  active: bool = True


class JobCreate(BaseModel):
  title: str
  location: str
  type: str
  summary: str
  active: bool = True


# _jobs: List[Job] = [
#   Job(id=1, title="Senior Full-Stack Engineer", location="Mohali · Hybrid", type="Full-time", summary="Own complex builds end-to-end."),
#   Job(id=2, title="Applied AI Engineer", location="Remote (India)", type="Full-time", summary="Build AI systems for pricing, forecasting and dev tools."),
# ]

def require_admin(token: str = Depends(lambda: None)):
  # very simple: expect Authorization: Bearer <token>
  from fastapi import Request
  from fastapi import Depends

  async def inner(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
      raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ", 1)[1]
    try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    except JWTError:
      raise HTTPException(status_code=401, detail="Invalid token")
    return True

  return Depends(inner)


@router.get("", response_model=List[Jobs])
async def list_jobs(db: Session = Depends(get_db)):
  jobs = db.query(Job).filter(Job.active == True).all()
  return jobs


# @router.post("", response_model=Job)
# async def create_job(payload: JobCreate, _: bool = require_admin()):
#   new_id = max([job.id for job in _jobs] or [0]) + 1
#   job = Job(id=new_id, **payload.dict())
#   _jobs.append(job)
#   return job


# @router.put("/{job_id}", response_model=Job)
# async def update_job(job_id: int, payload: JobCreate, _: bool = require_admin()):
#   for idx, job in enumerate(_jobs):
#     if job.id == job_id:
#       updated = Job(id=job_id, **payload.dict())
#       _jobs[idx] = updated
#       return updated
#   raise HTTPException(status_code=404, detail="Job not found")


# @router.delete("/{job_id}")
# async def delete_job(job_id: int, _: bool = require_admin()):
#   global _jobs
#   _jobs = [j for j in _jobs if j.id != job_id]
#   return {"ok": True}
