from __future__ import annotations

from collections import Counter

import emoji


EMOJI_MAP = {
    "😊": "joy",
    "😂": "joy",
    "😍": "joy",
    "🥳": "joy",
    "😄": "joy",
    "😢": "sadness",
    "😭": "sadness",
    "💔": "sadness",
    "😞": "sadness",
    "😡": "anger",
    "😠": "anger",
    "🤬": "anger",
    "😐": "neutral",
    "😶": "neutral",
    "😮": "surprise",
    "😲": "surprise",
    "😱": "surprise",
    "😟": "concern",
    "😰": "concern",
    "😬": "concern",
    "🔥": "intensity_boost",
    "💯": "intensity_boost",
    "⚡": "intensity_boost",
}


def extract_emojis(text: str) -> list[str]:
    return [char for char in text if char in emoji.EMOJI_DATA]


def remove_emojis(text: str) -> str:
    return "".join(char for char in text if char not in emoji.EMOJI_DATA)


def boost_emotion_with_emojis(
    text: str,
    base_emotion: str,
    model_confidence: float,
) -> dict[str, float | int | str]:
    emojis = extract_emojis(text)
    mapped = [EMOJI_MAP[item] for item in emojis if item in EMOJI_MAP]
    counts = Counter(item for item in mapped if item != "intensity_boost")

    emoji_emotion = max(counts, key=counts.get) if counts else None
    boost_count = mapped.count("intensity_boost")
    intensity = model_confidence + (0.1 * len(emojis)) + (0.15 * boost_count)

    final_emotion = base_emotion
    if emoji_emotion and emoji_emotion != base_emotion:
        intensity += 0.1
        final_emotion = emoji_emotion
    elif emoji_emotion:
        intensity += 0.05 * counts[emoji_emotion]
        final_emotion = emoji_emotion

    intensity = max(0.5, min(round(intensity, 2), 1.8))

    return {
        "emotion": final_emotion,
        "intensity": intensity,
        "emoji_emotion": emoji_emotion or "none",
        "emoji_count": len(emojis),
        "emoji_boost": round(0.1 * len(emojis) + 0.15 * boost_count, 2),
    }
