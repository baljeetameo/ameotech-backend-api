from __future__ import annotations

"""
Architecture Blueprint Tool Engine

Deterministic rule-based engine to recommend an architecture tier, stack and roadmap.
No ML, no external services. Pure functions for easy testing.
"""

from typing import Dict, List, Any, Optional


# --------------------------------------------------------------------
# Basic helpers
# --------------------------------------------------------------------


def _clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


def _norm_str(value: Optional[str]) -> str:
    if not value:
      return ""
    return str(value).strip().lower()


# --------------------------------------------------------------------
# Scoring functions
# --------------------------------------------------------------------


def score_expected_users(expected_users: str) -> int:
    v = _norm_str(expected_users)
    mapping = {
        "<1k": 20,
        "1k-10k": 35,
        "10k-100k": 55,
        "100k-1m": 75,
        "1m+": 90,
    }
    return mapping.get(v, 35)


def score_concurrency(concurrency: str) -> int:
    v = _norm_str(concurrency)
    mapping = {
        "<10": 15,
        "10-100": 30,
        "100-500": 55,
        "500-2000": 75,
        "2000+": 90,
    }
    return mapping.get(v, 30)


def score_traffic_pattern(traffic_pattern: str) -> int:
    v = _norm_str(traffic_pattern)
    mapping = {
        "steady": 30,
        "seasonal": 45,
        "bursty": 65,
        "unpredictable": 75,
    }
    return mapping.get(v, 30)


def score_data_size(data_size: str) -> int:
    v = _norm_str(data_size)
    mapping = {
        "<5gb": 20,
        "5-50gb": 35,
        "50-500gb": 55,
        "500gb-5tb": 75,
        "5tb+": 90,
    }
    return mapping.get(v, 35)


def score_data_type(data_type: str) -> int:
    v = _norm_str(data_type)
    mapping = {
        "transactional": 40,
        "analytics-heavy": 55,
        "logs & telemetry": 65,
        "media files": 70,
    }
    return mapping.get(v, 40)


def score_realtime(realtime: str) -> int:
    v = _norm_str(realtime)
    mapping = {
        "none": 10,
        "basic_realtime": 45,
        "basic-realtime": 45,
        "heavy_realtime": 75,
        "heavy-realtime": 75,
    }
    return mapping.get(v, 10)


def score_multi_tenancy(multi_tenancy: str) -> int:
    v = _norm_str(multi_tenancy)
    mapping = {
        "no": 10,
        "soft_multi_tenant": 40,
        "soft-multi-tenant": 40,
        "hard_multi_tenant": 70,
        "hard-multi-tenant": 70,
    }
    return mapping.get(v, 10)


def score_integrations(integrations: str) -> int:
    v = _norm_str(integrations)
    mapping = {
        "few": 20,
        "many": 45,
        "mission_critical": 70,
        "mission-critical": 70,
    }
    return mapping.get(v, 20)


def score_compliance(compliance: str) -> int:
    v = _norm_str(compliance)
    mapping = {
        "none": 10,
        "gdpr": 40,
        "hipaa": 65,
        "soc2": 55,
        "fintech": 70,
    }
    return mapping.get(v, 10)


def score_uptime(uptime: str) -> int:
    v = _norm_str(uptime)
    mapping = {
        "99%": 20,
        "99.5%": 35,
        "99.9%": 60,
        "99.99%": 80,
    }
    return mapping.get(v, 35)


def score_deployment(deployment: str) -> int:
    v = _norm_str(deployment)
    mapping = {
        "cloud": 40,
        "on_prem": 60,
        "on-prem": 60,
        "hybrid": 70,
    }
    return mapping.get(v, 40)


# --------------------------------------------------------------------
# Light "intelligent" inference from free text (optional)
# --------------------------------------------------------------------


def infer_from_description(description: str) -> Dict[str, Any]:
    """
    Optional helper to adjust some hints from a free-text description.
    This is still deterministic — just keyword checks.
    """
    text = _norm_str(description)

    hints: Dict[str, Any] = {}

    if not text:
        return hints

    # Product type hints
    if any(w in text for w in ["saas", "subscription", "b2b", "b2c"]):
        hints["product_type"] = "saas"
    elif any(w in text for w in ["ecommerce", "shop", "cart", "checkout"]):
        hints["product_type"] = "ecommerce"
    elif any(w in text for w in ["internal tool", "backoffice", "back-office", "ops team"]):
        hints["product_type"] = "internal_tool"
    elif any(w in text for w in ["marketplace", "multi-vendor", "two-sided", "two sided"]):
        hints["product_type"] = "marketplace"

    # Realtime hints
    if any(w in text for w in ["chat", "messaging", "websocket", "live update", "live-updates"]):
        hints["realtime"] = "basic_realtime"
    if any(w in text for w in ["trading", "realtime bidding", "realtime dashboard", "live feed"]):
        hints["realtime"] = "heavy_realtime"

    # Multi-tenancy hints
    if any(w in text for w in ["multi-tenant", "multi tenant", "multi company", "multi-organisation", "multi-organization"]):
        hints["multi_tenancy"] = "soft_multi_tenant"

    return hints


# --------------------------------------------------------------------
# Score aggregation and tier decision
# --------------------------------------------------------------------


def aggregate_scores(payload: dict) -> Dict[str, int]:
    """
    Compute category scores (0–100) for:
    - load
    - data
    - features
    - risk
    """

    # Load
    load_expected = score_expected_users(payload.get("expected_users", "1k-10k"))
    load_conc = score_concurrency(payload.get("concurrency", "10-100"))
    load_traffic = score_traffic_pattern(payload.get("traffic_pattern", "steady"))
    load_score = int(0.5 * load_expected + 0.3 * load_conc + 0.2 * load_traffic)

    # Data
    data_volume = score_data_size(payload.get("data_size", "5-50GB"))
    data_kind = score_data_type(payload.get("data_type", "transactional"))
    data_score = int(0.6 * data_volume + 0.4 * data_kind)

    # Features
    feat_realtime = score_realtime(payload.get("realtime", "none"))
    feat_multi = score_multi_tenancy(payload.get("multi_tenancy", "no"))
    feat_integrations = score_integrations(payload.get("integrations", "few"))
    features_score = int(0.4 * feat_realtime + 0.3 * feat_multi + 0.3 * feat_integrations)

    # Risk (compliance + uptime + deployment complexity)
    compliance_score = score_compliance(payload.get("compliance", "none"))
    uptime_score = score_uptime(payload.get("uptime", "99.5%"))
    deploy_score = score_deployment(payload.get("deployment", "cloud"))
    risk_score = int(0.4 * compliance_score + 0.4 * uptime_score + 0.2 * deploy_score)

    return {
        "load": _clamp(load_score),
        "data": _clamp(data_score),
        "features": _clamp(features_score),
        "risk": _clamp(risk_score),
    }


def decide_tier(scores: Dict[str, int]) -> Dict[str, Any]:
    """
    Decide the architecture tier based on weighted average of sub-scores.
    """
    weighted = (
        0.35 * scores["load"]
        + 0.25 * scores["data"]
        + 0.2 * scores["features"]
        + 0.2 * scores["risk"]
    )
    overall = _clamp(int(weighted))

    if overall < 40:
        tier = "A"
        label = "Lightweight / Early-stage"
        description = (
            "A single-region, cost-conscious architecture is likely sufficient for now. "
            "You can start with a well-structured monolith or modular backend and keep "
            "infrastructure simple while validating the product."
        )
    elif overall < 60:
        tier = "B"
        label = "Standard SaaS / Scale-up"
        description = (
            "You are in the range where a standard SaaS architecture makes sense — "
            "clear layering, background jobs, caching and observability, with room to "
            "scale as usage grows."
        )
    elif overall < 80:
        tier = "C"
        label = "Enterprise / High-scale"
        description = (
            "Your requirements suggest higher scale, stricter uptime or more complex data needs. "
            "You should lean into a service-oriented design with queues, observability and "
            "strong separation of concerns."
        )
    else:
        tier = "D"
        label = "Mission-critical / Platform"
        description = (
            "You are in a mission-critical range — high uptime, compliance, scale or multi-tenancy "
            "likely drive the need for a more distributed, resilient architecture with strong SRE practices."
        )

    return {
        "tier": tier,
        "label": label,
        "overall_score": overall,
        "description": description,
    }


# --------------------------------------------------------------------
# Stack & infra recommendations
# --------------------------------------------------------------------


def recommend_backend_stack(product_type: str, tier: str, compliance: str) -> List[str]:
    p = _norm_str(product_type)
    c = _norm_str(compliance)
    items: List[str] = []

    # Base language / runtime
    items.append(".NET 8 Web API for core services")
    items.append("PostgreSQL as primary relational datastore")

    # Message queues / async
    if tier in ("B", "C", "D"):
        items.append("Background job processing (e.g., Hangfire or equivalent)")
    if tier in ("C", "D"):
        items.append("Message broker for async workflows (e.g., Kafka, RabbitMQ or Azure Service Bus)")

    # Compliance-specific notes
    if c in ("hipaa", "fintech", "soc2"):
        items.append("Strict secrets management (e.g., cloud KMS) and audited access controls")
        items.append("Isolated environments for staging / production with clear promotion paths")

    # Product-type specifics (only lightly adjust)
    if p == "ecommerce":
        items.append("Idempotent order processing pipeline")
        items.append("Payment gateway integrations behind a clear boundary")
    elif p == "marketplace":
        items.append("Clear separation between buyer, seller and admin contexts")
    elif p == "internal_tool":
        items.append("Strong integration layer for internal systems (APIs, ETL or event-based)")

    return items


def recommend_frontend_stack(product_type: str, realtime: str, seo_needed: bool = False) -> List[str]:
    p = _norm_str(product_type)
    r = _norm_str(realtime)
    items: List[str] = []

    # Base recommendation
    if seo_needed or p in ("ecommerce", "marketing_site"):
        items.append("React + Next.js with TypeScript for SEO-friendly web")
    else:
        items.append("React + Vite with TypeScript for main web application")

    # Mobile / app-like experiences
    if p in ("mobile_app", "saas"):
        items.append("Optional: React Native for mobile clients where needed")

    # Realtime hints
    if r in ("basic_realtime", "heavy_realtime"):
        items.append("WebSocket or WebRTC-based channels for realtime experiences")

    return items


def recommend_infra_pattern(
    tier: str,
    deployment: str,
    traffic_pattern: str,
    realtime: str,
) -> Dict[str, Any]:
    d = _norm_str(deployment)
    t = _norm_str(traffic_pattern)
    r = _norm_str(realtime)

    result: Dict[str, Any] = {
        "compute": "",
        "database": "Managed PostgreSQL instance",
        "caching": "",
        "queueing": "",
        "observability": "",
        "deployment_model": "",
    }

    # Compute & deployment model
    if d == "on_prem":
        result["deployment_model"] = "Kubernetes or container orchestrator on-prem"
        result["compute"] = "Containerised .NET services managed via K8s"
    else:
        # Cloud or hybrid
        result["deployment_model"] = "Managed cloud environment (AWS, Azure or GCP)"
        if tier == "A":
            result["compute"] = "Single-region containerised app service or small VM set"
        elif tier == "B":
            result["compute"] = "Auto-scaling app service or container orchestrator (e.g., ECS, AKS)"
        else:
            result["compute"] = "Multi-AZ container orchestrator with separate system and data planes"

    # Caching
    if tier in ("B", "C", "D"):
        result["caching"] = "Distributed cache (e.g., Redis) for sessions and hot data"

    # Queueing
    if tier in ("B", "C", "D"):
        result["queueing"] = "Managed queue / topic system for background work and integrations"

    # Observability
    if tier in ("A", "B"):
        result["observability"] = "Centralised logging + basic metrics / dashboards"
    else:
        result["observability"] = "Structured logging, traces and metrics via OpenTelemetry-compatible stack"

    # Realtime + traffic-specific tweaks
    if r in ("basic_realtime", "heavy_realtime") or t in ("bursty", "unpredictable"):
        result["compute"] += " with autoscaling tuned for bursty workloads"

    return result


def estimate_infra_cost_band(tier: str) -> str:
    if tier == "A":
        return "$30–$150/month (excluding third-party SaaS tools)"
    if tier == "B":
        return "$200–$800/month (excluding third-party SaaS tools)"
    if tier == "C":
        return "$1,000–$5,000/month (depending on regions and data volume)"
    return "$8,000+/month (multi-region, high-uptime, compliance-heavy setups)"


# --------------------------------------------------------------------
# Risks & roadmap
# --------------------------------------------------------------------


def identify_risks(payload: dict, scores: Dict[str, int], tier: str) -> List[Dict[str, str]]:
    risks: List[Dict[str, str]] = []

    # High load but low risk score might indicate missing observability / resilience
    if scores["load"] >= 70 and scores["risk"] < 60:
        risks.append({
            "area": "Reliability",
            "title": "High expected load with limited reliability safeguards",
            "detail": (
                "You anticipate significant usage but your risk profile suggests limited attention to "
                "uptime, compliance or deployment resilience. Plan for observability, error budgets and "
                "clear rollback strategies early."
            ),
        })

    # Data-heavy but low data foundations
    if scores["data"] >= 65:
        risks.append({
            "area": "Data",
            "title": "Data volume and complexity require deliberate modelling",
            "detail": (
                "Your data volume and type suggest that you should invest in sane data modelling, "
                "partitioning and a path to warehousing/analytics rather than relying only on the main OLTP database."
            ),
        })

    # Realtime or multi-tenancy
    realtime = _norm_str(payload.get("realtime", "none"))
    multi = _norm_str(payload.get("multi_tenancy", "no"))
    compliance = _norm_str(payload.get("compliance", "none"))

    if realtime in ("basic_realtime", "heavy_realtime"):
        risks.append({
            "area": "Realtime",
            "title": "Realtime features add operational complexity",
            "detail": (
                "Live updates, chat or trading-style interactions need careful handling around state, "
                "backpressure and failure modes. Design dedicated channels and fallbacks for these paths."
            ),
        })

    if multi in ("soft_multi_tenant", "hard_multi_tenant"):
        risks.append({
            "area": "Multi-tenancy",
            "title": "Multi-tenant architecture decisions are hard to reverse",
            "detail": (
                "How you isolate tenants (schema, database or cluster level) has implications for cost, "
                "compliance and future refactors. It is worth spending time on this decision upfront."
            ),
        })

    if compliance in ("hipaa", "fintech", "soc2", "gdpr"):
        risks.append({
            "area": "Compliance",
            "title": "Regulatory requirements affect architecture",
            "detail": (
                "Compliance will impact data residency, logging, access control and change management. "
                "Make sure these constraints are reflected in your design and infrastructure choices from the start."
            ),
        })

    # Tier D reminder
    if tier == "D":
        risks.append({
            "area": "Operations",
            "title": "Mission-critical systems need operational maturity",
            "detail": (
                "At this level, you should plan for on-call rotations, incident management, capacity planning "
                "and regular disaster recovery exercises."
            ),
        })

    return risks


def build_roadmap(tier: str) -> List[str]:
    if tier == "A":
        return [
            "Weeks 1–2: Clarify core domain, user journeys and a clean modular backend structure.",
            "Weeks 3–4: Implement the core workflows with basic observability and a single-region deployment.",
            "Months 2–3: Introduce background jobs and refine data model as usage patterns become clearer.",
        ]
    if tier == "B":
        return [
            "Weeks 1–3: Lock architecture boundaries, database schema and integration strategy.",
            "Weeks 4–8: Build core services, introduce background processing and caching where needed.",
            "Months 3–6: Strengthen observability, add performance testing and plan a path towards data warehousing.",
        ]
    if tier == "C":
        return [
            "Weeks 1–4: Architecture blueprint with service boundaries, messaging patterns and data strategy.",
            "Months 2–4: Implement core services, message flows and observability with staging and pre-production environments.",
            "Months 4–9: Optimise for scale, introduce advanced caching, sharding/partitioning and resilience patterns.",
        ]
    return [
        "Weeks 1–4: Detailed platform and operations design, including SLOs, error budgets and compliance mapping.",
        "Months 2–6: Implement core platform services with multi-region deployment and robust observability.",
        "Months 6–12: Mature SRE practices, regular load testing, chaos experiments and continuous optimisation.",
    ]


# --------------------------------------------------------------------
# Public entrypoint
# --------------------------------------------------------------------


def run_architecture_blueprint(payload: dict) -> dict:
    """
    Main entrypoint for the Architecture Blueprint Tool.

    Input:
        payload: dict from the Labs wizard, optionally including 'description'.

    Output:
        dict with:
            - tier: 'A' | 'B' | 'C' | 'D'
            - overview: { tier, label, overall_score, description }
            - scores: { load, data, features, risk }
            - backend_stack: [str]
            - frontend_stack: [str]
            - infra: { ... }
            - risks: [ { area, title, detail } ]
            - roadmap: [str]
            - cost_band: str
    """

    # Optional light inference from free text
    description = payload.get("description") or payload.get("free_text") or ""
    inferred = infer_from_description(description)

    # inferred overrides nothing critical, just gives defaults where missing
    merged = {**payload, **inferred}

    scores = aggregate_scores(merged)
    overview = decide_tier(scores)

    backend_stack = recommend_backend_stack(
        product_type=merged.get("product_type", "saas"),
        tier=overview["tier"],
        compliance=merged.get("compliance", "none"),
    )
    frontend_stack = recommend_frontend_stack(
        product_type=merged.get("product_type", "saas"),
        realtime=merged.get("realtime", "none"),
        seo_needed=_norm_str(merged.get("seo_needed", "")) in ("yes", "true", "1"),
    )
    infra = recommend_infra_pattern(
        tier=overview["tier"],
        deployment=merged.get("deployment", "cloud"),
        traffic_pattern=merged.get("traffic_pattern", "steady"),
        realtime=merged.get("realtime", "none"),
    )
    cost_band = estimate_infra_cost_band(overview["tier"])
    risks = identify_risks(merged, scores, overview["tier"])
    roadmap = build_roadmap(overview["tier"])

    return {
        "tier": overview["tier"],
        "overview": overview,
        "scores": scores,
        "backend_stack": backend_stack,
        "frontend_stack": frontend_stack,
        "infra": infra,
        "risks": risks,
        "roadmap": roadmap,
        "cost_band": cost_band,
    }
