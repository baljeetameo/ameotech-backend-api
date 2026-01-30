# backend/app/reasoning/analyzer.py

from typing import Dict
import re

from .utils import normalize


def analyze_message(message: str) -> Dict:
    """
    Light-weight, deterministic analyzer.
    No ML, simple pattern-based classification.
    Returns a dict with:
      - original
      - clean
      - message_type
      - tone
      - is_rejection
      - is_meta
    """

    original = message or ""
    clean = normalize(original)

    msg_type = "normal"
    tone = "neutral"
    is_rejection = False
    is_meta = False

    # ---------------------------
    # Confusion / clarification
    # ---------------------------
    confusion_markers = [
        "what do you mean",
        "not clear",
        "don't understand",
        "do not understand",
        "explain again",
        "say again",
        "come again",
        "you mean what",
    ]
    if any(phrase in clean for phrase in confusion_markers):
        msg_type = "confused"
        tone = "uncertain"

    # ---------------------------
    # Rejection of suggestion / tool
    # ---------------------------
    rejection_patterns = [
        r"\bno\b",
        r"\bno thanks\b",
        r"\bnot now\b",
        r"\bdon't want\b",
        r"\bdo not want\b",
        r"\bstop\b",
        r"\bskip\b",
        r"\bleave it\b",
    ]
    if any(re.search(pat, clean) for pat in rejection_patterns):
        is_rejection = True

    # ---------------------------
    # Insults / strong negative
    # ---------------------------
    insult_markers = [
        "dumb", "stupid", "idiot", "useless", "scam", "fraud",
        "you suck", "terrible bot", "worst bot", "you are still dummy",
    ]
    if any(word in clean for word in insult_markers):
        msg_type = "insult"
        tone = "frustrated"

    # ---------------------------
    # Trust / legitimacy questions
    # ---------------------------
    trust_markers = [
        "can i trust",
        "can we trust",
        "are you legit",
        "are you real",
        "is this real",
        "is this a scam",
        "are you a scam",
        "are you fraud",
        "is ameotech legit",
        "is ameotech real",
        "are you guys real",
        "you guys real",
    ]
    if any(phrase in clean for phrase in trust_markers):
        msg_type = "trust"
        tone = "cautious"
        is_meta = True

    # ---------------------------
    # Bot / AI meta talk
    # ---------------------------
    bot_markers = [
        "chatgpt", "gpt", "ai bot", "are you ai", "are you a bot",
        "you a bot", "you are bot", "llm", "large language model",
    ]
    if any(word in clean for word in bot_markers):
        is_meta = True
        if msg_type == "normal":
            msg_type = "meta"

    # ---------------------------
    # Fallback tone
    # ---------------------------
    if msg_type == "normal" and not tone:
        tone = "neutral"

    return {
        "original": original,
        "clean": clean,
        "message_type": msg_type,
        "tone": tone,
        "is_rejection": is_rejection,
        "is_meta": is_meta,
    }
