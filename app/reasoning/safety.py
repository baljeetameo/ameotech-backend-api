"""
Safety utilities: input normalisation & basic profanity filtering.
"""

import re


PROFANITY = [
    "fuck", "shit", "bastard", "asshole",
]


def sanitize_input(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    # Normalise whitespace
    t = re.sub(r"\s+", " ", t)

    lower = t.lower()
    for bad in PROFANITY:
        if bad in lower:
            t = re.sub(bad, "***", t, flags=re.IGNORECASE)

    return t
