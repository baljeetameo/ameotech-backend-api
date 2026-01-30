from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr



class SuggestedReply(BaseModel):
  id: str
  label: str


class ChatSessionCreateResponse(BaseModel):
  session_id: str
  welcome: str
  suggestions: List[SuggestedReply]


class ChatMessageRequest(BaseModel):
  session_id: str
  message: str


class ChatMessageResponse(BaseModel):
  reply: str
  suggestions: List[SuggestedReply] = []


class ContentType(str):
  CASE_STUDY = "case_study"
  JOB_POST = "job_post"


class ContentStatus(str):
  DRAFT = "draft"
  PUBLISHED = "published"
  ARCHIVED = "archived"


class ContentItemBase(BaseModel):
  type: str
  title: str
  slug: str
  excerpt: Optional[str] = None
  body_rich: str
  tags: Optional[list[str]] = None
  meta: Optional[dict] = None


class ContentItem(ContentItemBase):
  id: str
  status: str


class ContentItemCreate(ContentItemBase):
  status: Optional[str] = ContentStatus.DRAFT


class ContentListResponse(BaseModel):
  items: list[ContentItem]

# ----------------------
# Labs: Product & Engineering Audit
# ----------------------


class AuditScores(BaseModel):
  product: int
  engineering: int
  data_ai: int


class AuditRecommendation(BaseModel):
  area: str
  title: str
  detail: str


class AuditRequest(BaseModel):
  product_stage: str
  release_freq: str
  tech_stack: Optional[str] = None
  ci_cd: bool
  testing: str
  data_centralized: bool
  analytics: str
  pain_points: List[str] = []


class AuditResponse(BaseModel):
  scores: AuditScores
  recommendations: List[AuditRecommendation]


# ----------------------
# Labs: Build Cost & Delivery Model Estimator
# ----------------------


class EstimatorScores(BaseModel):
  complexity: int
  urgency: int
  team: int
  budget: int


class EstimatorRequest(BaseModel):
  project_types: List[str]
  urgency: str
  company_stage: str
  team: str
  budget: str


class EstimatorResponse(BaseModel):
  model: str
  budget: str
  timeline: str
  scores: EstimatorScores
  plan: List[str]
  recommendations: List[str]



# ----------------------
# Labs: Architecture Blueprint Tool
# ----------------------


class ArchitectureBlueprintRequest(BaseModel):
  # Step 1 – Basic product
  product_type: Optional[str] = "saas"  # saas / mobile_app / ecommerce / internal_tool / marketplace
  expected_users: str                   # <1k / 1k-10k / 10k-100k / 100k-1M / 1M+
  traffic_pattern: str                  # steady / bursty / seasonal / unpredictable

  # Step 2 – Data & load
  data_size: str                        # <5GB / 5-50GB / 50-500GB / 500GB-5TB / 5TB+
  data_type: str                        # transactional / analytics-heavy / logs & telemetry / media files
  concurrency: str                      # <10 / 10-100 / 100-500 / 500-2000 / 2000+

  # Step 3 – Features
  realtime: str                         # none / basic_realtime / heavy_realtime
  multi_tenancy: str                    # no / soft_multi_tenant / hard_multi_tenant
  integrations: str                     # few / many / mission_critical

  # Step 4 – Constraints
  compliance: str                       # none / gdpr / hipaa / soc2 / fintech
  deployment: str                       # cloud / on_prem / hybrid
  uptime: str                           # 99% / 99.5% / 99.9% / 99.99%

  # Optional free-text + SEO hint
  description: Optional[str] = None
  seo_needed: Optional[bool] = False


class ArchitectureRiskItem(BaseModel):
  area: str
  title: str
  detail: str


class ArchitectureInfraConfig(BaseModel):
  compute: str
  database: str
  caching: Optional[str] = ""
  queueing: Optional[str] = ""
  observability: Optional[str] = ""
  deployment_model: Optional[str] = ""


class ArchitectureOverview(BaseModel):
  tier: str
  label: str
  overall_score: int
  description: str


class ArchitectureBlueprintResponse(BaseModel):
  tier: str
  overview: ArchitectureOverview
  scores: Dict[str, int]
  backend_stack: List[str]
  frontend_stack: List[str]
  infra: ArchitectureInfraConfig
  risks: List[ArchitectureRiskItem]
  roadmap: List[str]
  cost_band: str







class ChatMessageOut(BaseModel):
    id: int
    session_id: str
    sender: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True  # <-- Enable from_orm/from_attributes
    }


class ChatMessageReadUpdate(BaseModel):
    session_id: str
    is_read: bool


class ChatSessionOut(BaseModel):
    session_id: str
    is_read: bool
    messages: List[ChatMessageOut]

class MeetingRequest(BaseModel):
  name: str
  datetime: datetime
  meeting_link: Optional[str]

class ScheduleRequest(BaseModel):
  name: str
  email: str
  datetime: str   # ISO format
  user_access_token: str

class MeetingResponse(BaseModel):
  id: int
  name: str
  email: str
  meeting_datetime: datetime
  meeting_id: str
  join_url: str
  start_url: str


class DiscoverySprintCreate(BaseModel):
  name: str
  email: EmailStr
  company: Optional[str]
  role: Optional[str]

  project_type: str
  industry: Optional[str]
  budget_range: Optional[str]
  timeline: Optional[str]
  project_stage: Optional[str]

  has_existing_system: bool = False
  preferred_tech: Optional[str]
  pain_points: Optional[str]