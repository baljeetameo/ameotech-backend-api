from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, func, TIMESTAMP
from sqlalchemy.orm import declarative_base
import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    is_hr = Column(Boolean, default=False)
    is_sales_engineer = Column(Boolean, default=False)
    is_end_user = Column(Boolean, default=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False)
    sender = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    active = Column(Boolean, default=True)

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    meeting_datetime = Column(TIMESTAMP, nullable=False)
    meeting_id = Column(String(50), nullable=False)
    join_url = Column(Text, nullable=False)
    start_url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default="NOW()")

class DiscoverySprint(Base):
    __tablename__ = "discovery_sprints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    role = Column(String, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    google_meet_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DiscoverySprintRequest(Base):
    __tablename__ = "discovery_sprint_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    company = Column(String(150))
    role = Column(String(100))

    project_type = Column(String(50), nullable=False)
    industry = Column(String(100))
    budget_range = Column(String(50))
    timeline = Column(String(50))
    project_stage = Column(String(50))

    has_existing_system = Column(Boolean, default=False)
    preferred_tech = Column(Text)
    pain_points = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
