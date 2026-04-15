from __future__ import annotations

import re


WORD_RE = re.compile(r"\b[\w']+\b")
STRETCH_RE = re.compile(r"(.)\1{2,}", re.IGNORECASE)


def analyze_text_signals(text: str) -> dict[str, object]:
    words = WORD_RE.findall(text)
    exclamation_count = text.count("!")
    question_count = text.count("?")
    uppercase_words = sum(1 for word in words if len(word) > 1 and word.isupper())
    stretched_words = sum(1 for word in words if STRETCH_RE.search(word))

    boost = 0.0
    notes: list[str] = []

    if exclamation_count:
        exclamation_boost = min(0.24, 0.08 * exclamation_count)
        boost += exclamation_boost
        notes.append(f"Exclamation marks increased emphasis by {exclamation_boost:.2f}.")

    if question_count:
        question_boost = min(0.08, 0.04 * question_count)
        boost += question_boost
        notes.append(f"Question marks added conversational lift of {question_boost:.2f}.")

    if uppercase_words:
        uppercase_boost = min(0.18, 0.06 * uppercase_words)
        boost += uppercase_boost
        notes.append(f"Uppercase words increased intensity by {uppercase_boost:.2f}.")

    if stretched_words:
        stretch_boost = min(0.2, 0.07 * stretched_words)
        boost += stretch_boost
        notes.append(f"Stretched words increased expressiveness by {stretch_boost:.2f}.")

    return {
        "intensity_boost": round(boost, 2),
        "notes": notes,
        "counts": {
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "uppercase_words": uppercase_words,
            "stretched_words": stretched_words,
        },
    }
