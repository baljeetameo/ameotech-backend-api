
from typing import Dict, List

def _score_product(stage: str, release_freq: str) -> int:
  score = 50
  stage_weights = {
    "idea": 20,
    "mvp": 40,
    "early_revenue": 55,
    "growth": 75,
    "scaleup": 85,
  }
  freq_weights = {
    "ad_hoc": -15,
    "monthly": 0,
    "biweekly": 10,
    "weekly": 20,
    "daily": 25,
  }
  score = stage_weights.get(stage, 40)
  score += freq_weights.get(release_freq, 0)
  return max(0, min(100, score))


def _score_engineering(ci_cd: bool, testing: str) -> int:
  base = 30
  if ci_cd:
    base += 25
  testing_weights = {
    "none": 0,
    "low": 15,
    "medium": 30,
    "high": 45,
  }
  base += testing_weights.get(testing, 10)
  return max(0, min(100, base))


def _score_data_ai(data_centralized: bool, analytics: str) -> int:
  base = 20
  if data_centralized:
    base += 25
  analytics_weights = {
    "none": 0,
    "basic": 15,
    "intermediate": 30,
    "advanced": 45,
  }
  base += analytics_weights.get(analytics, 10)
  return max(0, min(100, base))


def _build_recommendations(scores: Dict[str, int], pain_points: List[str]):
  recs = []

  if scores["product"] < 50:
    recs.append({
      "area": "Product",
      "title": "Stabilise product & release cadence",
      "detail": "Clarify product milestones and move toward a predictable release rhythm (bi-weekly or weekly) before layering in heavy AI work."
    })
  else:
    recs.append({
      "area": "Product",
      "title": "You can safely invest in deeper AI / data work",
      "detail": "Your product maturity looks solid enough to support more advanced AI and data initiatives without derailing core delivery."
    })

  if scores["engineering"] < 50:
    recs.append({
      "area": "Engineering",
      "title": "Invest in CI/CD and automated testing",
      "detail": "Introduce CI/CD and at least smoke/critical path tests so changes ship more safely and you can iterate faster on AI and data features."
    })
  else:
    recs.append({
      "area": "Engineering",
      "title": "Leverage strong engineering foundations",
      "detail": "Your engineering baseline is good. Use it to run faster experiments, feature flags and safe rollouts for AI-powered capabilities."
    })

  if scores["data_ai"] < 50:
    recs.append({
      "area": "Data & AI",
      "title": "Centralise data and improve analytics",
      "detail": "Focus on getting a single source of truth (warehouse / lake) and reliable dashboards before training heavier ML models."
    })
  else:
    recs.append({
      "area": "Data & AI",
      "title": "Move from reporting to optimisation",
      "detail": "You have the foundations to start using ML and optimisation techniques in pricing, forecasting or workflow automation."
    })

  if pain_points:
    recs.append({
      "area": "Execution",
      "title": "Tackle your highest-friction delivery issues first",
      "detail": "Address pain points like slow releases, scattered data or manual processes with targeted improvements over the next 4–8 weeks."
    })

  return recs


def run_audit(payload: dict) -> dict:
  product = _score_product(payload.get("product_stage", ""), payload.get("release_freq", ""))
  engineering = _score_engineering(payload.get("ci_cd", False), payload.get("testing", "low"))
  data_ai = _score_data_ai(payload.get("data_centralized", False), payload.get("analytics", "basic"))

  scores = {
    "product": product,
    "engineering": engineering,
    "data_ai": data_ai,
  }

  recs = _build_recommendations(scores, payload.get("pain_points", []) or [])

  return {
    "scores": scores,
    "recommendations": recs,
  }
