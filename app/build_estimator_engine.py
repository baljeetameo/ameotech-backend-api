from typing import Dict, List


def score_complexity(types: List[str]) -> int:
  m = 0
  for t in types:
    t = t.strip()
    if t == "Pricing / Forecasting / Optimization":
      m = max(m, 90)
    elif t == "Add AI to existing system":
      m = max(m, 80)
    elif t == "Modernize legacy platform":
      m = max(m, 75)
    elif t == "Data engineering / warehouse":
      m = max(m, 70)
    elif t == "Build a new product":
      m = max(m, 60)
    elif t == "Workflow automation":
      m = max(m, 45)
    else:
      m = max(m, 50)
  return m


def score_urgency(u: str) -> int:
  mapping = {
    "4-6": 90,
    "8-12": 60,
    "future": 20,
  }
  return mapping.get(u, 20)


def score_team(t: str) -> int:
  mapping = {
    "none": 20,
    "small": 40,
    "strong": 70,
    "mature": 90,
  }
  return mapping.get(t, 40)


def score_budget(b: str) -> int:
  mapping = {
    "exploring": 20,
    "5-10": 40,
    "10-20": 60,
    "20-40": 80,
    "40+": 100,
  }
  return mapping.get(b, 20)


def determine_model(scores: Dict[str, int]) -> str:
  if scores["budget"] < 50:
    return "Discovery Sprint Only"
  if scores["complexity"] > 75 and scores["budget"] >= 80:
    return "AI Pod Retainer"
  if scores["urgency"] > 70:
    return "Hybrid (Sprint → Pod)"
  return "Discovery Sprint → Fixed Project"


def determine_budget_band(model: str) -> str:
  if model == "Discovery Sprint Only":
    return "$6K–$8K"
  if model == "AI Pod Retainer":
    return "$20K–$40K+/mo"
  if model == "Hybrid (Sprint → Pod)":
    return "$6K–$8K + $15K–$20K/mo"
  return "$10K–$20K initial"


def determine_timeline(scores: Dict[str, int]) -> str:
  if scores["urgency"] > 70:
    return "4–6 weeks"
  if scores["urgency"] > 40:
    return "8–12 weeks"
  return "Flexible"


def build_plan(model: str) -> List[str]:
  if model == "Discovery Sprint Only":
    return [
      "Week 1–2: Architecture & technical discovery",
      "Week 2–3: Scope definition & delivery roadmap",
      "Week 3–4: Implementation plan & proposal",
    ]
  if model == "AI Pod Retainer":
    return [
      "Month 1: Architecture, platform foundations & first vertical slice",
      "Month 2–3: Core feature delivery with tight feedback loops",
      "Month 4+: Scaling, optimisation and deeper AI use-cases",
    ]
  if model == "Hybrid (Sprint → Pod)":
    return [
      "Week 1–3: Discovery Sprint to de-risk assumptions",
      "Week 4–10: Build & integrate priority features",
      "Month 3+: Pod to operate, iterate and extend",
    ]
  return [
    "Week 1–2: Discovery Sprint",
    "Week 2–8: Fixed-scope build for initial value",
    "Week 8–12: Hardening, QA and go-live support",
  ]


def build_recommendations(model: str, scores: Dict[str, int]) -> List[str]:
  """
  Returns human-readable recommendation strings so they fit EstimatorResponse.recommendations: List[str].
  """
  rec_dicts: List[Dict[str, str]] = []

  if model == "Discovery Sprint Only":
    rec_dicts.append({
      "area": "Scope",
      "title": "Start with a focused Discovery Sprint",
      "detail": "Use a 2–3 week Discovery Sprint to clarify scope, architecture and success metrics before committing to a larger build."
    })
  elif model == "AI Pod Retainer":
    rec_dicts.append({
      "area": "Engagement",
      "title": "Treat this as a long-term platform, not a project",
      "detail": "An AI Pod gives you ongoing senior engineering capacity to ship, stabilise and extend your AI systems as your roadmap evolves."
    })
  elif model == "Hybrid (Sprint → Pod)":
    rec_dicts.append({
      "area": "Risk management",
      "title": "Use Sprint to de-risk, then the Pod to scale",
      "detail": "De-risk unknowns in a Sprint, then transition into a pod that owns delivery, optimisation and iteration."
    })
  else:
    rec_dicts.append({
      "area": "Delivery",
      "title": "Combine Sprint with a fixed delivery window",
      "detail": "Use a short Sprint to align on architecture, then a time-boxed build to deliver an MVP that proves value."
    })

  if scores["complexity"] >= 70:
    rec_dicts.append({
      "area": "Architecture",
      "title": "Invest early in the architecture",
      "detail": "High-complexity work repays upfront architecture. Clarify domain boundaries, data flows and failure modes before scaling the team."
    })

  if scores["team"] <= 40:
    rec_dicts.append({
      "area": "Team",
      "title": "Augment your team with senior leadership",
      "detail": "Pair your existing team with senior engineers / architects who can own the hard decisions and unblock delivery."
    })

  if scores["budget"] < 40:
    rec_dicts.append({
      "area": "Budget",
      "title": "Tight budget: prioritise one thin slice",
      "detail": "Focus on a narrow, high-leverage slice that proves ROI instead of spreading effort across too many initiatives."
    })

  # Flatten to strings for the API schema
  rec_strings: List[str] = []
  for r in rec_dicts:
    area = r.get("area", "").strip()
    title = r.get("title", "").strip()
    detail = r.get("detail", "").strip()

    parts: List[str] = []
    if area:
      parts.append(f"[{area}]")
    if title:
      parts.append(title)
    if detail:
      parts.append(detail)

    rec_strings.append(" – ".join(parts))

  return rec_strings


def run_estimator(payload: dict) -> dict:
  scores = {
    "complexity": score_complexity(payload.get("project_types") or []),
    "urgency": score_urgency(payload.get("urgency", "future")),
    "team": score_team(payload.get("team", "small")),
    "budget": score_budget(payload.get("budget", "exploring")),
  }
  model = determine_model(scores)
  return {
    "model": model,
    "budget": determine_budget_band(model),
    "timeline": determine_timeline(scores),
    "scores": scores,
    "plan": build_plan(model),
    "recommendations": build_recommendations(model, scores),
  }
