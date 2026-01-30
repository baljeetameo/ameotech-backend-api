from difflib import SequenceMatcher


def normalize(text: str) -> str:
    return (text or "").lower().strip()


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()
