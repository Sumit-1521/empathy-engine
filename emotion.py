from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from transformers import pipeline


MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"
ALIAS_MAP = {
    "joy": "joy",
    "sadness": "sadness",
    "anger": "anger",
    "neutral": "neutral",
    "fear": "concern",
    "surprise": "surprise",
    "love": "joy",
    "disgust": "anger",
    "concern": "concern",
}

KEYWORDS = {
    "joy": {
        "happy",
        "great",
        "awesome",
        "excited",
        "love",
        "yay",
        "glad",
        "hurray",
        "hooray",
        "won",
        "win",
        "victory",
        "celebrate",
        "success",
    },
    "sadness": {"sad", "upset", "cry", "lonely", "miss", "hurt", "sorry"},
    "anger": {"angry", "mad", "hate", "furious", "annoyed", "rage"},
    "surprise": {"wow", "unbelievable", "suddenly", "unexpected", "shocked", "amazing", "surprised"},
    "concern": {"worried", "concerned", "careful", "anxious", "nervous", "unsure", "risk"},
}


@lru_cache(maxsize=1)
def _emotion_pipeline():
    return pipeline("text-classification", model=MODEL_NAME, top_k=None)


def normalize_emotion(label: str) -> str:
    return ALIAS_MAP.get(label.lower(), "neutral")


def _fallback_detect(text: str) -> dict[str, Any]:
    lowered = text.lower()
    scores = {"joy": 0, "sadness": 0, "anger": 0, "surprise": 0, "concern": 0}

    for emotion, words in KEYWORDS.items():
        scores[emotion] = sum(1 for word in words if word in lowered)

    if max(scores.values(), default=0) == 0:
        return {"emotion": "neutral", "confidence": 0.55, "source": "fallback"}

    emotion = max(scores, key=scores.get)
    confidence = min(0.95, 0.6 + 0.1 * scores[emotion])
    return {"emotion": emotion, "confidence": round(confidence, 2), "source": "fallback"}


def use_huggingface_model() -> bool:
    value = os.getenv("EMPATHY_USE_HF_MODEL", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def detect_emotion(text: str) -> dict[str, Any]:
    if not use_huggingface_model():
        return _fallback_detect(text)

    try:
        classifier = _emotion_pipeline()
        predictions = classifier(text)
        ranked = predictions[0] if predictions and isinstance(predictions[0], list) else predictions
        top = max(ranked, key=lambda item: item["score"])
        return {
            "emotion": normalize_emotion(top["label"]),
            "confidence": round(float(top["score"]), 2),
            "source": MODEL_NAME,
        }
    except Exception:
        return _fallback_detect(text)
