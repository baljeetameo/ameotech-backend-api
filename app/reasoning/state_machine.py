"""
ARE-3.5 State Machine
Deterministic conversation flow controller.
Prevents loops, handles escalation, and guides user into correct domain.
"""

from typing import Dict


class StateMachine:

    VALID_STATES = {
        "unknown",
        "new_project",
        "existing_system",
        "careers",
        "pricing_engine",
        "data_platform",
        "contact_human",
        "handoff_ready",
    }

    def __init__(self):
        pass

    def transition(self, current: str, intent: str, analysis: Dict, session) -> str:
        """
        Resolve next state based on:
        - current state
        - detected intent
        - user tone/frustration
        - message type
        """

        message_type = analysis.get("message_type")

        # Hard escalation triggers
        if intent == "contact_human":
            return "contact_human"

        if session.frustration_level >= 4:
            return "handoff_ready"

        # Direct intent → state mapping
        direct_map = {
            "new_project": "new_project",
            "existing_system": "existing_system",
            "careers": "careers",
            "pricing_engine": "pricing_engine",
            "data_platform": "data_platform",
        }

        if intent in direct_map:
            session.mode = direct_map[intent]
            session.set_goal(intent)
            session.reset_clarifier()
            return direct_map[intent]

        # Unknown intent handling
        if intent == "unknown":
            loops = session.increment_clarifier()

            if session.mode:
                return session.mode

            if loops >= 2:
                return "handoff_ready"

            return "unknown"

        # Meta / confusion
        if message_type in ["confused", "meta"]:
            if session.mode:
                return session.mode
            return "unknown"

        # Insults
        if message_type == "insult":
            if session.mode:
                return session.mode
            return "unknown"

        # Default fallback
        if session.mode:
            return session.mode

        return "unknown"
