# backend/app/chatbot.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from jose import jwt, JWTError

from .auth import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session, declarative_base
from .models import Job
from app.database import get_db
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
import openai
from openai.error import RateLimitError

Base = declarative_base()

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

#from openai import OpenAI

# client = OpenAI(
#   api_key="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"
# )


openai.api_key = "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" #"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"

class CompanyService(Base):
    __tablename__ = "company_services"
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, index=True)
    description = Column(Text)

class ChatbotQuery(Base):
    __tablename__ = "chatbot_queries"
    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_service_by_message(db: Session, message: str):
    return db.query(CompanyService).filter(
        CompanyService.service_name.ilike(f"%{message}%")
    ).first()

def get_previous_query(db: Session, message: str):
    return db.query(ChatbotQuery).filter(
        ChatbotQuery.user_query.ilike(f"%{message}%")
    ).first()

def save_new_query(db: Session, user_query: str, response: str):
    new_entry = ChatbotQuery(user_query=user_query, response=response)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry



class UserMessage(BaseModel):
    message: str

@router.post("")
def chat(payload: UserMessage, db: Session = Depends(get_db)):
    message = payload.message.lower()

    # 1. Check predefined company services
    service = get_service_by_message(db, message)
    if service:
        return {"response": service.description}

    # 2. Check previously stored queries
    previous = get_previous_query(db, message)
    if previous:
        return {"response": previous.response}

    # 3. Fallback to ChatGPT
    try:
      chat_response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": "You are a helpful IT company assistant."},
              {"role": "user", "content": message}
          ],
          max_tokens=300
      )
      answer = chat_response.choices[0].message["content"]
    except RateLimitError:
      # Fallback: return a friendly message or cached response
      answer = "Sorry, the AI service is currently busy. Please try again later."


    # 4. Save new query
    save_new_query(db, user_query=message, response=answer)

    return {"response": answer}