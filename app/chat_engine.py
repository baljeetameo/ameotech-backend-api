from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
import datetime as dt

from .schemas import SuggestedReply, ChatMessageResponse


@dataclass
class Message:
  role: str  # 'user' | 'assistant'
  content: str
  created_at: dt.datetime = field(default_factory=lambda: dt.datetime.utcnow())


@dataclass
class SessionState:
  id: str
  stage: str = "intro"
  created_at: dt.datetime = field(default_factory=lambda: dt.datetime.utcnow())
  updated_at: dt.datetime = field(default_factory=lambda: dt.datetime.utcnow())
  domain: Optional[str] = None
  company_size: Optional[str] = None
  urgency: Optional[str] = None
  budget: Optional[str] = None
  email: Optional[str] = None
  messages: List[Message] = field(default_factory=list)


class ChatEngine:
  """Simple rules-based chat flow for Ameotech website.

  Design goals:
  - Qualify leads for Discovery Sprint / AI Pod / Custom Project.
  - Keep structure explicit (no LLMs).
  - Suggest quick-reply buttons so users can move fast.
  """

  def __init__(self) -> None:
    self.sessions: Dict[str, SessionState] = {}

  # Session management ----------------------------------------------------- #

  def create_session(self) -> SessionState:
    session_id = str(uuid.uuid4())
    session = SessionState(id=session_id)
    self.sessions[session_id] = session
    return session

  def get_session(self, session_id: str) -> Optional[SessionState]:
    return self.sessions.get(session_id)

  # Chat flow -------------------------------------------------------------- #

  def handle_message(self, session_id: str, message_text: str) -> ChatMessageResponse:
    session = self.sessions.get(session_id)
    if not session:
      session = self.create_session()

    session.messages.append(Message(role="user", content=message_text))
    session.updated_at = dt.datetime.utcnow()

    # Normalise input for simple keyword rules
    text_lower = message_text.lower().strip()

    if session.stage == "intro":
      return self._handle_intro(session, text_lower)

    if session.stage == "domain":
      return self._handle_domain(session, text_lower)

    if session.stage == "company_size":
      return self._handle_company_size(session, text_lower)

    if session.stage == "urgency":
      return self._handle_urgency(session, text_lower)

    if session.stage == "budget":
      return self._handle_budget(session, text_lower)

    if session.stage == "email":
      return self._handle_email(session, text_lower)

    # Fallback small-talk-ish response (still deterministic)
    reply = (
      "Got it. If you share a bit more about your use case, I can recommend "
      "whether a discovery sprint, AI pod, or custom project is the best fit."
    )
    suggestions = self._default_suggestions()
    self._add_bot_message(session, reply)
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  # Stage handlers --------------------------------------------------------- #

  def initial_welcome(self, session: SessionState) -> ChatMessageResponse:
    reply = (
         "Hi, I'm the Ameotech assistant. I'll help you figure out the right way to work with us."
      "What are you mainly interested in right now?"
    )
    suggestions = [
      SuggestedReply(id="pricing", label="Dynamic pricing / revenue optimisation"),
      SuggestedReply(id="forecasting", label="Forecasting, analytics, or BI"),
      SuggestedReply(id="automation", label="Workflow automation / data pipelines"),
      SuggestedReply(id="platform", label="Custom AI platform / DevPilot OS"),
    ]
    self._add_bot_message(session, reply)
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  def _handle_intro(self, session: SessionState, text: str) -> ChatMessageResponse:
    # Very simple routing based on keywords, but suggestions give a clear path.
    if "price" in text or "pricing" in text:
      session.domain = "pricing"
    elif "forecast" in text or "demand" in text or "analytics" in text or "bi" in text:
      session.domain = "forecasting"
    elif "automation" in text or "workflow" in text or "rpa" in text:
      session.domain = "automation"
    elif "platform" in text or "devpilot" in text or "dev pilot" in text:
      session.domain = "platform"
    else:
      session.domain = "other"

    session.stage = "domain"
    return self._handle_domain(session, text)

  def _handle_domain(self, session: SessionState, text: str) -> ChatMessageResponse:
    domain = session.domain or "other"
    if domain == "pricing":
      intro = (
        "Great — pricing optimisation is one of our core strengths."
        "To calibrate things, where are you primarily operating today?"
      )
    elif domain == "forecasting":
      intro = (
        "Got it — forecasting and analytics. Those projects work best when we know the data reality."
        "What type of business are you running?"
      )
    elif domain == "automation":
      intro = (
        "Nice — workflow and decision automation unlock a lot of leverage."
        "Which area are you looking to automate first?"
      )
    elif domain == "platform":
      intro = (
        "You’re thinking about a custom AI platform / DevPilot-style setup. That’s where we go deep."
        "Roughly what stage is your product team at?"
      )
    else:
      intro = (
        "No problem — even if it doesn’t fit neatly in a box, we can usually map it to a clear track."
        "What best describes your company right now?"
      )

    reply = intro
    suggestions = [
      SuggestedReply(id="stage_saasp", label="VC-backed SaaS (growth)"),
      SuggestedReply(id="stage_mid", label="Mid-market / enterprise"),
      SuggestedReply(id="stage_early", label="Early-stage startup"),
      SuggestedReply(id="stage_other", label="Something else"),
    ]
    session.stage = "company_size"
    self._add_bot_message(session, reply)
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  def _handle_company_size(self, session: SessionState, text: str) -> ChatMessageResponse:
    if "saas" in text:
      session.company_size = "saas_growth"
    elif "mid" in text or "enterprise" in text:
      session.company_size = "mid_enterprise"
    elif "early" in text or "seed" in text or "pre" in text:
      session.company_size = "early"
    else:
      session.company_size = "other"

    session.stage = "urgency"
    reply = (
      "Helpful, thank you."
      "What does your timeline look like if we end up working together?"
    )
    suggestions = [
      SuggestedReply(id="timeline_now", label="We need to move in the next 2–4 weeks"),
      SuggestedReply(id="timeline_quarter", label="This quarter (exploring options)"),
      SuggestedReply(id="timeline_later", label="Just exploring / later"),
    ]
    self._add_bot_message(session, reply)
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  def _handle_urgency(self, session: SessionState, text: str) -> ChatMessageResponse:
    if "week" in text or "now" in text or "asap" in text:
      session.urgency = "immediate"
    elif "quarter" in text or "month" in text:
      session.urgency = "near_term"
    else:
      session.urgency = "exploring"

    session.stage = "budget"
    reply = (
      "Understood."
      "One last calibration: for the initial phase, which band feels closest to your current budget?"
    )
    suggestions = [
      SuggestedReply(id="budget_ds", label="USD 6K–10K (Discovery / pilot)"),
      SuggestedReply(id="budget_pod", label="USD 10K–20K/month (AI pod)"),
      SuggestedReply(id="budget_custom", label="Depends on scope"),
    ]
    self._add_bot_message(session, reply)
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  def _handle_budget(self, session: SessionState, text: str) -> ChatMessageResponse:
    if "6" in text or "10" in text or "pilot" in text or "discovery" in text:
      session.budget = "pilot"
    elif "20" in text or "pod" in text or "retainer" in text:
      session.budget = "pod"
    else:
      session.budget = "custom"

    session.stage = "email"
    recommendation = self._compute_recommendation(session)

    reply = (
      f"{recommendation}"
      "If you drop your work email here, we’ll follow up with a short note and a link to book time in the calendar."
    )
    suggestions: List[SuggestedReply] = [
      SuggestedReply(id="share_email", label="I’ll share my email"),
      SuggestedReply(id="no_email", label="Prefer not to share email here"),
    ]
    self._add_bot_message(session, reply)
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  def _handle_email(self, session: SessionState, text: str) -> ChatMessageResponse:
    # Very light heuristic: treat anything with "@" as an email.
    if "@" in text and "." in text:
      session.email = text.strip()
      reply = (
        "Perfect, thank you. We’ll review your answers and send a short note with a proposed next step "
        "and calendar link."
        "If there’s anything else you want us to know (links, context, constraints), you can drop it here."
      )
      suggestions: List[SuggestedReply] = [
        SuggestedReply(id="share_more", label="Share a bit more context"),
        SuggestedReply(id="done", label="That’s all for now"),
      ]
    else:
      reply = (
        "Totally fine if you’d rather not share an email. You can instead write to hello@ameotech.com whenever "
        "you’re ready, or book a call from the website."
        "Anything else you’d like to ask right now?"
      )
      suggestions = [
        SuggestedReply(id="ask_process", label="How do your sprints work?"),
        SuggestedReply(id="ask_pricing", label="How do you think about pricing?"),
      ]

    self._add_bot_message(session, reply)
    # Keep stage as email; user can still ask things, but we do not advance the structured flow further.
    return ChatMessageResponse(reply=reply, suggestions=suggestions)

  # Helpers ---------------------------------------------------------------- #

  def _add_bot_message(self, session: SessionState, content: str) -> None:
    session.messages.append(Message(role="assistant", content=content))
    session.updated_at = dt.datetime.utcnow()

  def _compute_recommendation(self, session: SessionState) -> str:
    domain = session.domain or "other"
    urgency = session.urgency or "exploring"
    budget = session.budget or "custom"

    if urgency == "immediate" and budget in {"pilot", "custom"}:
      track = "a 2–4 week Discovery Sprint to de-risk scope and architecture."
    elif budget == "pod":
      track = "an AI Pod retainer where we act as your senior applied AI team."
    elif domain == "pricing":
      track = "a pricing engine discovery + pilot on a focused subset of SKUs."
    else:
      track = "a short discovery phase to shape the first production-quality milestone."

    return (
      "Based on what you’ve shared, the most natural starting point is "
      f"{track} We keep the first engagement tightly scoped so we can prove value quickly."
    )

  def _default_suggestions(self) -> List[SuggestedReply]:
    return [
      SuggestedReply(id="ask_services", label="What kind of projects do you take on?"),
      SuggestedReply(id="ask_process", label="How do your sprints work?"),
    ]


chat_engine = ChatEngine()
