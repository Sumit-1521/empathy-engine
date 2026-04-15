from __future__ import annotations

import re

from emoji_utils import remove_emojis


CLAUSE_SPLIT_RE = re.compile(r"([.!?]+)")
WHITESPACE_RE = re.compile(r"\s+")


def _normalize_spacing(text: str) -> str:
    text = WHITESPACE_RE.sub(" ", text).strip()
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    return text


def _shape_clause(clause: str, emotion: str, intensity: float) -> str:
    trimmed = clause.strip(" ,")
    if not trimmed:
        return ""

    if emotion == "sadness":
        return trimmed
    if emotion == "anger" and intensity >= 1.0:
        return trimmed.upper()
    return trimmed


def prepare_speech_text(text: str, emotion: str, intensity: float) -> str:
    cleaned = _normalize_spacing(remove_emojis(text))
    if not cleaned:
        return ""

    parts = CLAUSE_SPLIT_RE.split(cleaned)
    clauses: list[str] = []

    for index in range(0, len(parts), 2):
        clause = parts[index].strip()
        if not clause:
            continue

        punctuation = parts[index + 1] if index + 1 < len(parts) else ""
        spoken_clause = _shape_clause(clause, emotion, intensity)

        if emotion == "joy":
            ending = "!" if intensity >= 0.95 else "."
        elif emotion == "anger":
            ending = "!" if punctuation or intensity >= 0.9 else "."
        elif emotion == "sadness":
            ending = "..." if index < len(parts) - 2 else "."
        else:
            ending = punctuation[:1] if punctuation else "."

        clauses.append(f"{spoken_clause}{ending}")

    speech_text = " ".join(item.strip() for item in clauses if item.strip())

    if emotion == "sadness":
        speech_text = speech_text.replace("...", "... ")
    elif emotion == "joy" and intensity >= 1.1:
        speech_text = speech_text.replace("! ", "!  ")

    return _normalize_spacing(speech_text)
