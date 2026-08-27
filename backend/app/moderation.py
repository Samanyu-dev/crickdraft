import re

# Minimal blocklist covering the most severe, unambiguous slurs. Not a
# general profanity filter - just a guard against the clearest abuse on a
# public leaderboard/username field.
_BLOCKED_TERMS = [
    "nigger", "nigga", "faggot", "retard", "chink", "spic", "kike", "tranny",
]

_LEET_MAP = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})


def _normalize(value: str) -> str:
    value = value.lower().translate(_LEET_MAP)
    return re.sub(r"[^a-z]", "", value)


def contains_blocked_term(username: str) -> bool:
    normalized = _normalize(username)
    return any(term in normalized for term in _BLOCKED_TERMS)
