"""
Humanizer: adjusts bot_reply slightly based on tone + frustration.
    No randomness. Pure rule-based tweaks.
"""

from typing import Dict


def humanize(text: str, session, analysis: Dict) -> str:
    tone = analysis.get("tone")
    msg_type = analysis.get("message_type")
    frustration = session.frustration_level

    # High frustration → add a calm, owning note
    if frustration >= 3:
        return (
            "Let me reset and make this clearer."
            + text
        )

    # Confused tone → acknowledge confusion
    if tone == "confused" or msg_type == "confused":
        return (
            "I might not have been clear earlier. "
            + text
        )

    # Angry → keep response short and steady
    if tone == "angry":
        return (
            "I understand this is frustrating. "
            + text
        )

    # Default: return as-is
    return text
