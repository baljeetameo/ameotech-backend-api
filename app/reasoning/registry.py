"""
Intent registry for ARE-3.5
Central place to manage intents and their keyword patterns.
"""

INTENT_REGISTRY = {
    "new_project": {
        "keywords": [
            "start a project", "new app", "new build", "build project",
            "create a system", "new idea", "startup idea",
            "build software", "new website", "new platform",
            "i want to build", "i have an idea", "new product",
            "mvp", "prototype"
        ],
        "synonyms": ["build", "create", "develop", "launch"],
        "pages": ["/services", "/ai", "/automation"],
        "weight": 1.0,
    },
    "existing_system": {
        "keywords": [
            "fix", "modify", "update", "upgrade", "enhance",
            "existing system", "existing app", "bug", "issue",
            "problem", "stuck", "broke", "maintenance",
            "legacy", "refactor"
        ],
        "synonyms": ["repair", "improve", "stabilise"],
        "pages": ["/services"],
        "weight": 1.0,
    },
    "careers": {
        "keywords": [
            "job", "jobs", "career", "hiring", "opening", "vacancy",
            "opning", "internship", "intern", "opportunity", "role",
            "position"
        ],
        "synonyms": ["resume", "cv", "apply"],
        "pages": ["/careers"],
        "weight": 1.2,
    },
    "pricing_engine": {
        "keywords": [
            "pricing", "elasticity", "optimizer", "skus", "price change",
            "forecast", "margin", "pricing engine", "discount",
            "promotion", "yield management"
        ],
        "synonyms": ["price", "demand", "skus"],
        "pages": ["/pricing", "/labs/pricing"],
        "weight": 1.1,
    },
    "data_platform": {
        "keywords": [
            "data", "analytics", "pipeline", "etl", "warehouse",
            "dashboard", "redshift", "snowflake", "bigquery",
            "data engineering", "lakehouse"
        ],
        "synonyms": ["analytics", "bi", "reporting"],
        "pages": ["/data"],
        "weight": 1.0,
    },
    "contact_human": {
        "keywords": [
            "talk to human", "talk to someone", "speak to someone",
            "book a call", "contact", "reach out", "call me",
            "someone real"
        ],
        "synonyms": ["human", "agent"],
        "pages": [],
        "weight": 1.5,
    },
    "unknown": {
        "keywords": [],
        "synonyms": [],
        "pages": [],
        "weight": 0.1,
    },
}
