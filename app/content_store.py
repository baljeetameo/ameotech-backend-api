from __future__ import annotations

import threading
import uuid
from typing import Dict, List, Optional

from .schemas import ContentItem, ContentItemCreate, ContentStatus, ContentType


class InMemoryContentStore:
  def __init__(self) -> None:
    self._items: Dict[str, ContentItem] = {}
    self._lock = threading.Lock()
    self._ensure_seed_data()

  def _ensure_seed_data(self) -> None:
    # Seed a couple of case studies and a sample job so the UI has something to show
    if self._items:
      return

    demo_items = [
      ContentItem(
        id=str(uuid.uuid4()),
        type=ContentType.CASE_STUDY,
        title="Dynamic Pricing at Enterprise Scale",
        slug="dynamic-pricing-walmart",
        excerpt="Large-scale dynamic pricing engine integrated with demand forecasting and competitive intelligence.",
        body_rich=(
          "Challenge: Manual pricing causing 2–3% margin loss monthly.\n"
          "Solution: ML-driven pricing engine with explicit margin guardrails and elasticity-based price moves.\n"
          "Result: 5–7% margin improvement across thousands of SKUs."
        ),
        tags=["Retail", "Pricing", "Enterprise"],
        meta={},
        status=ContentStatus.PUBLISHED,
      ),
      ContentItem(
        id=str(uuid.uuid4()),
        type=ContentType.CASE_STUDY,
        title="Demand Forecasting & Inventory Optimization",
        slug="demand-forecasting-wwe",
        excerpt="Forecast-driven inventory and supply planning for a global entertainment brand.",
        body_rich=(
          "Challenge: Overstock on seasonal inventory and inconsistent demand prediction.\n"
          "Solution: Hierarchical forecasting models feeding supply chain planning.\n"
          "Result: 18% reduction in overstock and improved cash flow."
        ),
        tags=["Entertainment", "Forecasting"],
        meta={},
        status=ContentStatus.PUBLISHED,
      ),
      ContentItem(
        id=str(uuid.uuid4()),
        type=ContentType.JOB_POST,
        title="Senior Backend Engineer (.NET / Python)",
        slug="senior-backend-engineer",
        excerpt="Work on applied AI systems: pricing engines, forecasting, and high-scale data pipelines.",
        body_rich=(
          "You will design and build backend services for pricing, forecasting, and data pipelines.\n"
          "You should be comfortable owning architecture, code quality, and mentoring other engineers."
        ),
        tags=["Engineering"],
        meta={
          "location": "Remote / India",
          "employment_type": "Full-time",
          "experience_level": "Senior",
          "apply_email": "careers@ameotech.com",
        },
        status=ContentStatus.PUBLISHED,
      ),
    ]

    for item in demo_items:
      self._items[item.id] = item

  def list_items(
    self,
    type: Optional[str] = None,
    status: Optional[str] = None,
  ) -> List[ContentItem]:
    with self._lock:
      items = list(self._items.values())
      if type:
        items = [i for i in items if i.type == type]
      if status:
        items = [i for i in items if i.status == status]
      return items

  def get_by_slug(self, type: str, slug: str, status: Optional[str] = None) -> Optional[ContentItem]:
    with self._lock:
      for item in self._items.values():
        if item.type == type and item.slug == slug:
          if status and item.status != status:
            continue
          return item
      return None

  def get(self, id: str) -> Optional[ContentItem]:
    with self._lock:
      return self._items.get(id)

  def create(self, data: ContentItemCreate) -> ContentItem:
    with self._lock:
      new_item = ContentItem(
        id=str(uuid.uuid4()),
        type=data.type,
        title=data.title,
        slug=data.slug,
        excerpt=data.excerpt or "",
        body_rich=data.body_rich,
        tags=data.tags or [],
        meta=data.meta or {},
        status=data.status or ContentStatus.DRAFT,
      )
      self._items[new_item.id] = new_item
      return new_item

  def update(self, id: str, data: ContentItemCreate) -> Optional[ContentItem]:
    with self._lock:
      existing = self._items.get(id)
      if not existing:
        return None
      existing.title = data.title
      existing.slug = data.slug
      existing.excerpt = data.excerpt or ""
      existing.body_rich = data.body_rich
      existing.tags = data.tags or []
      existing.meta = data.meta or {}
      if data.status:
        existing.status = data.status
      self._items[id] = existing
      return existing

  def set_status(self, id: str, status: str) -> Optional[ContentItem]:
    with self._lock:
      existing = self._items.get(id)
      if not existing:
        return None
      existing.status = status
      self._items[id] = existing
      return existing


STORE = InMemoryContentStore()
