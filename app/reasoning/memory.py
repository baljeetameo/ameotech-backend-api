import uuid
import time
from typing import Optional, Dict


class SessionMemory:
    """
    Central memory for each chat session.
    Tracks conversational state, user tone, frustration, topic, and last actions.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())

        # Finite-state machine state
        self.state: str = "unknown"

        # Intent tracking
        self.last_intent: Optional[str] = None
        self.last_confidence: float = 0.0

        # Conversation goal / lane
        # values like: "new_project", "existing_system", "careers", etc.
        self.goal: Optional[str] = None

        # User behaviour indicators
        self.frustration_level: int = 0      # increments on insults / confusion
        self.rejection_count: int = 0        # “no I don’t want that”
        self.clarifier_loops: int = 0        # prevent infinite loops

        # Tone: neutral / confused / angry / joking / etc.
        self.tone: str = "neutral"

        # Last bot action (open_lab_tool, clarify, escalate, etc.)
        self.last_action: Optional[str] = None

        # Mode memory (project/existing/careers)
        self.mode: Optional[str] = None

        # New project mini-state:
        # "intro"   → user just entered new_project lane
        # "idea"    → user is sharing / has shared the idea
        # "shaping" → user is discussing tech, budget, timelines, etc.
        self.new_project_stage: str = "intro"

        # Timestamp for analytics
        self.created_at = time.time()
        self.last_updated = time.time()

    def record_user_message(self):
        """Update basic timestamps."""
        self.last_updated = time.time()

    def update_from_analysis(self, analysis: Dict):
        """
        Sync tone, message types, and behavioural triggers with session.
        """

        self.record_user_message()

        message_type = analysis.get("message_type")
        tone = analysis.get("tone")

        # Tone update
        if tone:
            self.tone = tone

        # Frustration triggers
        if message_type == "insult":
            self.frustration_level += 2
        elif message_type in ["confused", "clarification_request"]:
            self.frustration_level += 1

        # Reject triggers
        if analysis.get("is_rejection"):
            self.rejection_count += 1

        # Clamp values
        self.frustration_level = min(self.frustration_level, 5)
        self.rejection_count = min(self.rejection_count, 5)
        self.clarifier_loops = min(self.clarifier_loops, 5)

    def reset_clarifier(self):
        """Restart clarifier loop when user gives meaningful input."""
        self.clarifier_loops = 0

    def increment_clarifier(self):
        """Prevent infinite clarification loops."""
        self.clarifier_loops += 1
        return self.clarifier_loops

    def set_goal(self, new_goal: Optional[str]):
        """Lock user goal once detected (lane, not the idea text)."""
        if new_goal and not self.goal:
            self.goal = new_goal

    def memory_snapshot(self) -> dict:
        """Useful for debugging—never for client display."""
        return {
            "session_id": self.session_id,
            "state": self.state,
            "last_intent": self.last_intent,
            "goal": self.goal,
            "frustration": self.frustration_level,
            "rejections": self.rejection_count,
            "tone": self.tone,
            "mode": self.mode,
            "new_project_stage": self.new_project_stage,
        }
