# backend/app/labs/ai_readiness_engine.py

from typing import Dict, List


def _score_data(selected: List[str]) -> int:
    score = 50
    if "Centralized warehouse" in selected:
        score += 20
    if "Historical data available" in selected:
        score += 15
    if "ETL pipelines in place" in selected:
        score += 10
    if "Data is scattered" in selected:
        score -= 20
    if "Mostly unstructured data" in selected:
        score -= 10
    if "Manual data cleaning required" in selected:
        score -= 5
    return max(0, min(100, score))


def _score_workflows(selected: List[str]) -> int:
    score = 50
    if "Repeatable process" in selected:
        score += 15
    if "API-ready" in selected:
        score += 20
    if "Event-driven" in selected:
        score += 15
    if "Mostly manual" in selected:
        score -= 20
    if "Excel/Email driven" in selected:
        score -= 10
    if "Legacy systems in place" in selected:
        score -= 10
    return max(0, min(100, score))


def _score_opportunities(selected: List[str]) -> int:
    # More opportunities = more potential
    base = 40
    score = base + len(selected) * 10
    return max(0, min(100, score))


def _score_org(stage: str, team: str) -> int:
    score = 40
    if stage == "startup":
        score += 0
    elif stage == "growth":
        score += 10
    elif stage == "mid":
        score += 15
    elif stage == "enterprise":
        score += 20

    if team == "none":
        score -= 10
    elif team == "small":
        score += 5
    elif team == "strong":
        score += 15
    elif team == "mature":
        score += 20

    return max(0, min(100, score))


def _score_constraints(budget: str, urgency: str) -> int:
    score = 50
    if budget == "low":
        score -= 15
    elif budget == "moderate":
        score += 0
    elif budget == "good":
        score += 10
    elif budget == "strong":
        score += 20

    if urgency == "fast":
        score -= 5  # more pressure
    elif urgency == "medium":
        score += 0
    elif urgency == "slow":
        score += 5

    return max(0, min(100, score))


def run_ai_readiness(form: Dict) -> Dict:
    data_maturity = form.get("data_maturity") or []
    workflow_maturity = form.get("workflow_maturity") or []
    ai_opportunities = form.get("ai_opportunities") or []
    org_stage = form.get("org_stage") or ""
    team_strength = form.get("team_strength") or ""
    budget = form.get("budget") or "moderate"
    urgency = form.get("urgency") or "medium"

    data_score = _score_data(data_maturity)
    workflow_score = _score_workflows(workflow_maturity)
    opp_score = _score_opportunities(ai_opportunities)
    org_score = _score_org(org_stage, team_strength)
    constraints_score = _score_constraints(budget, urgency)

    readiness = int(
        0.30 * data_score
        + 0.25 * workflow_score
        + 0.25 * opp_score
        + 0.20 * org_score
    )

    quick_wins: List[str] = []
    recommendations: List[Dict] = []

    # Quick wins based on gaps
    if data_score < 60:
        quick_wins.append("Stabilise data foundations and create a single source of truth.")
        recommendations.append(
            {
                "area": "Data",
                "detail": "Introduce a basic warehouse or lake, stop copying data manually between tools.",
            }
        )

    if workflow_score < 60:
        quick_wins.append("Document key workflows and introduce API-friendly entry points.")
        recommendations.append(
            {
                "area": "Workflows",
                "detail": "Identify 2–3 high-frequency flows and design them as repeatable, API-triggered steps.",
            }
        )

    if opp_score > 60:
        quick_wins.append("Prioritise 1–2 clear AI use cases instead of trying to do everything.")
        recommendations.append(
            {
                "area": "AI Opportunities",
                "detail": "Pick a lane (pricing, forecasting, or workflow automation) and design a focused PoC.",
            }
        )

    if org_score < 60:
        recommendations.append(
            {
                "area": "Organisation",
                "detail": "Strengthen ownership for AI: a clear sponsor plus a small cross-functional squad.",
            }
        )

    if not quick_wins:
        quick_wins.append("You have a decent base; the next step is choosing the right starting project.")

    # Decide next step
    next_step_text = ""
    next_actions: List[Dict] = []

    if data_score < 60 or workflow_score < 60 or org_score < 60:
        next_step_text = (
            "You’re not blocked from AI, but the safest move is to stabilise the architecture and data "
            "before committing to heavy AI work."
        )
        next_actions.append(
            {
                "label": "Run Architecture Blueprint",
                "type": "open_lab_tool",
                "target": "architecture_blueprint",
                "payload": {"lab_tool": "architecture_blueprint"},
            }
        )
        next_actions.append(
            {
                "label": "Talk to Ameotech",
                "type": "escalate_human",
                "payload": {"link": "mailto:hello@ameotech.com"},
            }
        )
    elif readiness >= 70 and constraints_score >= 60:
        next_step_text = (
            "You look reasonably ready for applied AI. It’s worth scoping a concrete project rather than "
            "doing more diagnostics."
        )
        next_actions.append(
            {
                "label": "Run Build Estimator",
                "type": "open_lab_tool",
                "target": "build_estimator",
                "payload": {"lab_tool": "build-estimator"},
            }
        )
        next_actions.append(
            {
                "label": "Schedule a working session",
                "type": "escalate_human",
                "payload": {"link": "mailto:hello@ameotech.com"},
            }
        )
    else:
        next_step_text = (
            "You’re in a mixed zone: there’s AI potential, but some constraints and gaps. A small, "
            "well-defined PoC or advisory sprint is usually the safest call."
        )
        next_actions.append(
            {
                "label": "Talk to Ameotech",
                "type": "escalate_human",
                "payload": {"link": "mailto:hello@ameotech.com"},
            }
        )

    scores = {
        "data": data_score,
        "workflows": workflow_score,
        "opportunities": opp_score,
        "org": org_score,
        "constraints": constraints_score,
        "score": readiness,
    }

    return {
        "scores": scores,
        "quick_wins": quick_wins,
        "recommendations": recommendations,
        "next_step": next_step_text,
        "next_actions": next_actions,
    }
