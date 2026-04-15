from __future__ import annotations


def _clamp_intensity(intensity: float) -> float:
    return max(0.5, min(intensity, 1.8))


def _to_percent(value: int) -> str:
    if value >= 0:
        return f"+{value}%"
    return f"{value}%"


def _to_hz(value: int) -> str:
    if value >= 0:
        return f"+{value}Hz"
    return f"{value}Hz"


def get_voice_profile(style: str) -> dict[str, str]:
    profiles = {
        "supportive": {
            "label": "Supportive",
            "voice": "en-US-JennyNeural",
            "description": "Warm and balanced for customer support demos.",
        },
        "energetic": {
            "label": "Energetic",
            "voice": "en-US-AriaNeural",
            "description": "Brighter delivery for upbeat or celebratory lines.",
        },
        "grounded": {
            "label": "Grounded",
            "voice": "en-US-GuyNeural",
            "description": "Steadier delivery for neutral or serious responses.",
        },
        "storyteller": {
            "label": "Storyteller",
            "voice": "en-US-EmmaNeural",
            "description": "Expressive narrative voice for longer passages.",
        },
        "executive": {
            "label": "Executive",
            "voice": "en-US-DavisNeural",
            "description": "Measured and polished delivery for business demos.",
        },
        "companion": {
            "label": "Companion",
            "voice": "en-US-AnaNeural",
            "description": "Gentler conversational voice for empathetic dialogue.",
        },
    }
    return profiles.get(style, profiles["supportive"])


def map_emotion_to_voice(emotion: str, intensity: float, style: str = "supportive") -> dict[str, float | int | str]:
    base_rate = 150
    normalized_intensity = _clamp_intensity(intensity)
    voice_profile = get_voice_profile(style)

    if emotion == "joy":
        rate = base_rate + int(40 * normalized_intensity)
        volume = min(1.0, 0.85 + (0.1 * normalized_intensity))
        pitch_hz = 40 + int(35 * normalized_intensity)
    elif emotion == "sadness":
        rate = base_rate - int(30 * normalized_intensity)
        volume = max(0.5, 0.8 - (0.08 * normalized_intensity))
        pitch_hz = -20 - int(20 * normalized_intensity)
    elif emotion == "anger":
        rate = base_rate + int(30 * normalized_intensity)
        volume = min(1.0, 0.9 + (0.08 * normalized_intensity))
        pitch_hz = 10 + int(20 * normalized_intensity)
    elif emotion == "surprise":
        rate = base_rate + int(35 * normalized_intensity)
        volume = min(1.0, 0.88 + (0.07 * normalized_intensity))
        pitch_hz = 55 + int(28 * normalized_intensity)
    elif emotion == "concern":
        rate = base_rate - int(12 * normalized_intensity)
        volume = max(0.55, 0.82 - (0.04 * normalized_intensity))
        pitch_hz = -5 + int(10 * normalized_intensity)
    else:
        rate = base_rate
        volume = 0.9
        pitch_hz = 0

    rate = max(90, min(rate, 240))
    volume = round(max(0.3, min(volume, 1.0)), 2)
    rate_percent = int(round(((rate - base_rate) / base_rate) * 100))
    volume_percent = int(round((volume - 1.0) * 100))

    return {
        "rate": rate,
        "volume": volume,
        "pitch_hz": pitch_hz,
        "edge_rate": _to_percent(rate_percent),
        "edge_volume": _to_percent(volume_percent),
        "edge_pitch": _to_hz(pitch_hz),
        "edge_voice": voice_profile["voice"],
        "voice_style": voice_profile["label"],
        "voice_description": voice_profile["description"],
    }
