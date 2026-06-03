import re
from difflib import SequenceMatcher


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]{3,}", text.lower())
    return set(words)


def jaccard_similarity(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def sequence_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def combined_similarity(a: str, b: str) -> float:
    return 0.6 * jaccard_similarity(a, b) + 0.4 * sequence_similarity(a, b)
