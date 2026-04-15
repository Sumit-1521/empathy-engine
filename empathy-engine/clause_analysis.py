from __future__ import annotations

import re

from emoji_utils import boost_emotion_with_emojis, remove_emojis
from emotion import detect_emotion
from speech_text import prepare_speech_text
from text_signals import analyze_text_signals
from voice_mapper import map_emotion_to_voice


CLAUSE_RE = re.compile(r"[^.!?]+[.!?]*")


def split_into_clauses(text: str) -> list[str]:
    clauses = [item.strip() for item in CLAUSE_RE.findall(text) if item.strip()]
    return clauses or ([text.strip()] if text.strip() else [])


def analyze_clauses(
    text: str,
    style: str = "supportive",
    dominant_emotion: str | None = None,
) -> list[dict[str, object]]:
    clauses = split_into_clauses(text)
    results: list[dict[str, object]] = []

    for index, clause in enumerate(clauses, start=1):
        cleaned_clause = remove_emojis(clause).strip()
        if not cleaned_clause:
            continue

        model_result = detect_emotion(clause)
        emoji_result = boost_emotion_with_emojis(
            clause,
            model_result["emotion"],
            model_result["confidence"],
        )
        signal_result = analyze_text_signals(clause)
        intensity = max(
            0.5,
            min(round(emoji_result["intensity"] + signal_result["intensity_boost"], 2), 1.8),
        )
        applied_emotion = dominant_emotion or str(emoji_result["emotion"])
        voice = map_emotion_to_voice(applied_emotion, intensity, style=style)
        speech_text = prepare_speech_text(clause, emoji_result["emotion"], intensity)
        results.append(
            {
                "index": len(results) + 1,
                "raw_text": clause,
                "speech_text": speech_text,
                "emotion": emoji_result["emotion"],
                "applied_emotion": applied_emotion,
                "confidence": model_result["confidence"],
                "intensity": intensity,
                "rate": voice["rate"],
                "pitch_hz": voice["pitch_hz"],
                "volume": voice["volume"],
                "edge_voice": voice["edge_voice"],
                "edge_rate": voice["edge_rate"],
                "edge_volume": voice["edge_volume"],
                "edge_pitch": voice["edge_pitch"],
            }
        )

    return results
