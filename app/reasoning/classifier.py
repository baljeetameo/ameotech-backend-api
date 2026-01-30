# backend/app/reasoning/classifier.py

"""
ARE-3.x Intent Classifier

Deterministic scoring:
- phrase / keyword scoring via INTENT_REGISTRY
- domain override rules (project vs existing vs careers)
- topic_hint extraction for router:
    - project_like
    - existing_like
    - careers_like
"""

from typing import Dict, Tuple

from .registry import INTENT_REGISTRY
from .utils import normalize, fuzzy_ratio


def _score_intents(message: str, page: str, session) -> Dict[str, float]:
    clean = normalize(message)
    page = page or "/"
    scores: Dict[str, float] = {}

    for intent, cfg in INTENT_REGISTRY.items():
        score = 0.0

        # Keyword hits
        for kw in cfg["keywords"]:
            if kw in clean:
                score += 1.0
            else:
                # fuzzy partial for longer words
                if len(kw) > 4 and fuzzy_ratio(clean, kw) > 0.8:
                    score += 0.6

        # Synonym hits
        for syn in cfg["synonyms"]:
            if syn in clean:
                score += 0.5

        # Page boosts
        for p in cfg["pages"]:
            if page.startswith(p):
                score += 0.4

        # Context reinforcement (light)
        if session.last_intent == intent:
            score += 0.2
        if session.goal == intent:
            score += 0.5

        score *= cfg.get("weight", 1.0)
        scores[intent] = score

    return scores


def detect_intent(
    message: str,
    analysis: Dict,
    session,
    page: str,
) -> Tuple[str, float, Dict[str, float]]:
    """
    Returns:
        final_intent: str
        final_confidence: float
        meta: dict (currently all_scores; analysis is also mutated to include topic_hint)
    """

    clean = normalize(message)
    scores = _score_intents(message, page, session)
    top_intent = max(scores, key=lambda k: scores[k])
    top_score = scores[top_intent]

    msg_type = analysis.get("message_type")
    is_rejection = analysis.get("is_rejection")
    is_meta = analysis.get("is_meta")

    # -----------------------------
    # Topic hint detection
    # -----------------------------
    # These hints are softer than full intent but guide the router.
    careers_hint_terms = [
        "job", "jobs", "opening", "openning", "career", "careers",
        "hiring", "vacancy", "internship", "intern", "position", "role",
    ]
    existing_hint_terms = [
        "existing system", "existing app", "legacy",
        "website", "web site", "site",
        "bug", "bugs", "issue", "issues", "error", "errors",
        "crash", "crashing", "down", "slow", "performance",
        "maintenance", "maintain", "support",
    ]
    project_hint_terms = [
        "project", "product", "app", "application", "platform",
        "saas", "tool", "solution", "idea", "mvp", "prototype",
    ]

    topic_hint = None
    if any(t in clean for t in careers_hint_terms):
        topic_hint = "careers_like"
    elif any(t in clean for t in existing_hint_terms):
        topic_hint = "existing_like"
    elif any(t in clean for t in project_hint_terms):
        topic_hint = "project_like"

    # Push topic_hint into analysis so router can see it
    analysis["clean"] = clean
    analysis["topic_hint"] = topic_hint

    # -----------------------------
    # 1. Meta questions override
    # -----------------------------
    if is_meta and msg_type not in ("trust",):
        # user is asking about the bot itself, not domain
        return "unknown", 0.3, scores

    # -----------------------------
    # 2. Insult handling
    # -----------------------------
    # We do NOT throw away semantics on insults anymore.
    # Only if frustration is high, we escalate directly.
    if msg_type == "insult":
        if session.frustration_level >= 3:
            return "contact_human", 0.9, scores
        # otherwise: continue with normal classification

    # -----------------------------
    # 3. Rejection override
    # -----------------------------
    if is_rejection:
        # If user rejects a tool but we know the mode (project/existing),
        # keep them in that lane instead of resetting.
        if session.mode in ["new_project", "existing_system"]:
            return session.mode, 0.6, scores
        return "unknown", 0.3, scores

    # -----------------------------
    # 4. Direct "talk to human"
    # -----------------------------
    human_triggers = [
        "talk to human",
        "talk to someone",
        "speak to someone",
        "someone real",
        "real person",
        "call me",
        "can you call",
    ]
    if any(k in clean for k in human_triggers):
        return "contact_human", 0.9, scores

    # -----------------------------
    # 5. Domain override rules
    # -----------------------------
    # Use stronger markers for hard routing; topic_hint is softer.
    careers_markers = careers_hint_terms

    project_markers = [
        "new project", "start a project", "start project",
        "build a project", "build product", "new product",
        "new saas", "new app", "mvp", "prototype", "launch an app",
    ]

    existing_markers = [
        "existing system", "existing app", "legacy",
        "website", "web site", "site",
        "bug", "bugs", "issue", "issues", "error", "errors",
        "crash", "crashing", "down", "slow", "performance",
        "maintenance", "maintain", "support",
    ]

    has_careers = any(m in clean for m in careers_markers)
    has_project_strong = any(m in clean for m in project_markers)
    has_existing = any(m in clean for m in existing_markers)

    # Generic "project" as a strong hint if not clearly careers
    generic_project = "project" in clean
    has_project = has_project_strong or (generic_project and not has_careers)

    # If message clearly looks like a system/website/app issue,
    # and does NOT look like careers → force existing_system.
    if has_existing and not has_careers:
        return "existing_system", 0.9, scores

    # If message clearly looks like a new build request,
    # and does NOT look like careers → force new_project.
    if has_project and not has_careers:
        return "new_project", 0.85, scores

    # -----------------------------
    # 6. Normal scoring with thresholds
    # -----------------------------

    # If top score is very low, try to soft-fallback to last intent if any.
    if top_score < 0.5:
        if session.last_intent:
            return session.last_intent, 0.4, scores
        return "unknown", top_score, scores

    # If top intent is "unknown" but we have a previous one, reuse it.
    if top_intent == "unknown" and session.last_intent:
        return session.last_intent, 0.4, scores

    return top_intent, top_score, scores
