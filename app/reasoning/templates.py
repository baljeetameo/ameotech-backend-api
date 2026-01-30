"""
ARE-3.5 Templates
Unified structures for engine responses.
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ActionObject:
    action: str
    bot_reply: str
    action_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemResponse:
    session_id: str
    intent: str
    intent_confidence: float
    action: str
    action_payload: Dict[str, Any]
    bot_reply: str
    meta: Dict[str, Any] = field(default_factory=dict)
