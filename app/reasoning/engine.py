# backend/app/reasoning/engine.py

"""
ARE-3.x — Ameotech Reasoning Engine
Deterministic multi-stage conversational pipeline.
No ML, no embeddings, no GPT at runtime.
"""

from .memory import SessionMemory
from .analyzer import analyze_message
from .classifier import detect_intent
from .state_machine import StateMachine
from .router import route_message
from .humanize import humanize
from .templates import SystemResponse
from .safety import sanitize_input


class ReasoningEngine:

    def __init__(self):
        self.sm = StateMachine()

    def process(self, session: SessionMemory, user_raw_message: str, page: str):
        """
        Main entrypoint for every message.
        Returns SystemResponse.
        """

        # 1. Clean + sanity check message
        user_message = sanitize_input(user_raw_message)

        # 2. Analyzer → extract structure & tone
        analysis = analyze_message(user_message)

        # 3. Determine intent with multi-scorer
        intent, confidence, meta_intents = detect_intent(
            message=user_message,
            analysis=analysis,
            session=session,
            page=page,
        )

        # 4. Update memory with analysis + intent
        session.update_from_analysis(analysis)
        session.last_intent = intent
        session.last_confidence = confidence

        # 5. State Machine: resolve current_state -> next_state
        next_state = self.sm.transition(
            current=session.state,
            intent=intent,
            analysis=analysis,
            session=session,
        )
        session.state = next_state

        # 6. Router decides: action + bot message template
        action_obj = route_message(
            state=next_state,
            intent=intent,
            confidence=confidence,
            session=session,
            analysis=analysis,
        )

        # Track last action to avoid repetition
        session.last_action = action_obj.action

        # 7. Humanize final output
        final_reply = humanize(
            text=action_obj.bot_reply,
            session=session,
            analysis=analysis,
        )

        # 8. Build output payload
        return SystemResponse(
            session_id=session.session_id,
            intent=intent,
            intent_confidence=confidence,
            action=action_obj.action,
            action_payload=action_obj.action_payload,
            bot_reply=final_reply,
        )
