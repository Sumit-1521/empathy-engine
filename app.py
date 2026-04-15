from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template, request

from clause_analysis import analyze_clauses
from emoji_utils import boost_emotion_with_emojis
from emotion import detect_emotion
from speech_text import prepare_speech_text
from text_signals import analyze_text_signals
from tts_engine import generate_audio, generate_segmented_audio
from voice_mapper import get_voice_profile, map_emotion_to_voice


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
EXPRESSIVE_OUTPUT_FILE = STATIC_DIR / "output_expressive.mp3"
BASELINE_OUTPUT_FILE = STATIC_DIR / "output_baseline.mp3"

app = Flask(__name__)

DEMO_PRESETS = [
    {
        "label": "Joy",
        "emotion": "joy",
        "examples": [
            "I was nervous before the game... but then we WON!!! This is unbelievable! 😊",
            "This is the best news I have heard all week. We actually did it!",
            "I cannot stop smiling today. Everything finally worked out for us!",
        ],
    },
    {
        "label": "Anger",
        "emotion": "anger",
        "examples": [
            "Why did you do this??? I trusted you, and now I am really upset! 😡",
            "This keeps happening again and again, and I am honestly furious now.",
            "I asked for one simple thing, so why was it ignored?",
        ],
    },
    {
        "label": "Sadness",
        "emotion": "sadness",
        "examples": [
            "I miss those days... everything feels quieter now, and I still think about them. 😢",
            "It is hard to explain, but the room feels empty without them here.",
            "I thought I was okay, but tonight everything feels heavy again.",
        ],
    },
    {
        "label": "Surprise",
        "emotion": "surprise",
        "examples": [
            "Wait... we got the contract approved today? That is unbelievable! 😮",
            "No way, the results came in already? I was not expecting that at all.",
            "I opened the email and just froze. I could not believe what I saw.",
        ],
    },
    {
        "label": "Concern",
        "emotion": "concern",
        "examples": [
            "I am not sure this will work yet. We should be careful before we promise anything. 😟",
            "Something feels off here, and I think we need to double-check the risks.",
            "I am worried we are moving too fast without enough information.",
        ],
    },
    {
        "label": "Mixed Story",
        "emotion": "mixed",
        "examples": [
            "The meeting started badly, but by the end we found a solution and I finally felt hopeful.",
            "We lost the first round. Everyone looked worried. Then we came back and won the final match!!! 🔥",
            "At first I thought the deal was gone, but then the client smiled and said yes.",
        ],
    },
]

VOICE_STYLES = [
    {"value": "supportive", **get_voice_profile("supportive")},
    {"value": "energetic", **get_voice_profile("energetic")},
    {"value": "grounded", **get_voice_profile("grounded")},
    {"value": "storyteller", **get_voice_profile("storyteller")},
    {"value": "executive", **get_voice_profile("executive")},
    {"value": "companion", **get_voice_profile("companion")},
]


def recommend_voice_style(emotion: str) -> str:
    if emotion == "joy":
        return "energetic"
    if emotion == "anger":
        return "grounded"
    if emotion == "sadness":
        return "companion"
    if emotion == "surprise":
        return "storyteller"
    if emotion == "concern":
        return "supportive"
    return "executive"


def intensity_label(intensity: float) -> str:
    if intensity >= 1.3:
        return "High"
    if intensity >= 0.9:
        return "Medium"
    return "Low"


def should_anchor_clause_voice(final_emotion: str, clause_count: int) -> bool:
    return clause_count > 1 and final_emotion in {"joy", "sadness", "anger", "surprise", "concern"}


def build_analysis(text: str, voice_style: str) -> dict[str, object]:
    model_result = detect_emotion(text)
    emoji_result = boost_emotion_with_emojis(text, model_result["emotion"], model_result["confidence"])
    signal_result = analyze_text_signals(text)

    final_intensity = max(
        0.5,
        min(
            round(emoji_result["intensity"] + signal_result["intensity_boost"], 2),
            1.8,
        ),
    )
    raw_clause_result = analyze_clauses(text, style=voice_style)
    anchor_voice = should_anchor_clause_voice(emoji_result["emotion"], len(raw_clause_result))
    clause_result = analyze_clauses(
        text,
        style=voice_style,
        dominant_emotion=emoji_result["emotion"] if anchor_voice else None,
    )

    voice_settings = map_emotion_to_voice(
        emoji_result["emotion"],
        final_intensity,
        style=voice_style,
    )
    speech_text = " ".join(clause["speech_text"] for clause in clause_result) or prepare_speech_text(
        text,
        emoji_result["emotion"],
        final_intensity,
    )

try:
    if len(clause_result) > 1:
        expressive_segments = [
            {
                "text": str(clause["speech_text"]),
                "voice": str(clause["edge_voice"]),
                "rate": str(clause["edge_rate"]),
                "volume": str(clause["edge_volume"]),
                "pitch": str(clause["edge_pitch"]),
            }
            for clause in clause_result
        ]

        baseline_segments = [
            {
                "text": str(clause["speech_text"]),
                "voice": str(voice_settings["edge_voice"]),
                "rate": "+0%",
                "volume": "+0%",
                "pitch": "+0Hz",
            }
            for clause in clause_result
        ]

        baseline_result = generate_segmented_audio(
            segments=baseline_segments,
            output_path=BASELINE_OUTPUT_FILE,
            fallback_rate=150,
            fallback_volume=0.9,
        )

        expressive_result = generate_segmented_audio(
            segments=expressive_segments,
            output_path=EXPRESSIVE_OUTPUT_FILE,
            fallback_rate=voice_settings["rate"],
            fallback_volume=voice_settings["volume"],
        )

    else:
        baseline_result = generate_audio(
            text=speech_text,
            rate=150,
            volume=0.9,
            output_path=BASELINE_OUTPUT_FILE,
        )

        expressive_result = generate_audio(
            text=speech_text,
            rate=voice_settings["rate"],
            volume=voice_settings["volume"],
            output_path=EXPRESSIVE_OUTPUT_FILE,
        )

except Exception as e:
    print("🔥 AUDIO ERROR:", e)

    expressive_result = {
        "fallback_path": "output_expressive.mp3",
        "mime_type": "audio/mpeg",
        "backend": "fallback"
    }

    baseline_result = {
        "fallback_path": "output_baseline.mp3",
        "mime_type": "audio/mpeg"
    }
    return {
        "text": text,
        "model_emotion": model_result["emotion"],
        "model_confidence": model_result["confidence"],
        "model_source": model_result["source"],
        "emoji_emotion": emoji_result["emoji_emotion"],
        "emoji_count": emoji_result["emoji_count"],
        "emoji_boost": emoji_result["emoji_boost"],
        "final_emotion": emoji_result["emotion"],
        "final_intensity": final_intensity,
        "voice_settings": voice_settings,
        "signal_boost": signal_result["intensity_boost"],
        "signal_notes": signal_result["notes"],
        "signal_counts": signal_result["counts"],
        "speech_text": speech_text,
        "clauses": clause_result,
        "audio_file": expressive_result.get("fallback_path", "output_expressive.mp3"),
        "baseline_audio_file": baseline_result.get("fallback_path", "output_baseline.mp3"),
        "audio_mime_type": expressive_result["mime_type"],
        "baseline_audio_mime_type": baseline_result["mime_type"],
        "tts_backend": expressive_result["backend"],
        "voice_style": voice_settings["voice_style"],
        "voice_description": voice_settings["voice_description"],
        "recommended_voice_style": get_voice_profile(recommend_voice_style(emoji_result["emotion"]))["label"],
        "intensity_label": intensity_label(final_intensity),
        "intensity_percent": int(round((final_intensity / 1.8) * 100)),
        "voice_anchor_mode": anchor_voice,
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", presets=DEMO_PRESETS, voice_styles=VOICE_STYLES, selected_voice="supportive")


@app.route("/generate", methods=["POST"])
def generate():
    text = request.form.get("text", "").strip()
    voice_style = request.form.get("voice_style", "supportive").strip() or "supportive"
    if not text:
        return render_template(
            "index.html",
            error="Enter some text to generate speech.",
            presets=DEMO_PRESETS,
            voice_styles=VOICE_STYLES,
            selected_voice=voice_style,
        )

    try:
        result = build_analysis(text, voice_style)
    except Exception as exc:  # pragma: no cover - defensive for runtime UI stability
        return render_template(
            "index.html",
            error=f"Generation failed: {exc}",
            text=text,
            presets=DEMO_PRESETS,
            voice_styles=VOICE_STYLES,
            selected_voice=voice_style,
        )

    return render_template(
        "index.html",
        result=result,
        text=text,
        presets=DEMO_PRESETS,
        voice_styles=VOICE_STYLES,
        selected_voice=voice_style,
    )


import os

if __name__ == "__main__":
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
