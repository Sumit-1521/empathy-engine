# Empathy Engine

Empathy Engine converts text into emotionally expressive speech by combining NLP-based emotion detection, emoji-aware intensity boosting, and rule-based speech modulation. The goal is to simulate prosody control with an explainable offline pipeline.

HERE IS THE DEPLOYED URL -https://empathy-engine-ik30.onrender.com

## Core Concept

This project sits at the intersection of affective computing and prosody.

- Affective computing gives the system a way to infer emotional state from natural language.
- Prosody shapes how speech sounds through pacing, loudness, and vocal emphasis.
- The application simulates prosody control with rule-based adjustments to speech rate and volume.

## Architecture

```text
User Input (Text with optional Emojis)
        ↓
Emotion Detection (ML Model)
        ↓
Emoji Emotion Booster
        ↓
Final Emotion + Intensity Score
        ↓
Voice Mapping Engine
        ↓
TTS Engine (pyttsx3)
        ↓
Audio Output (.wav)
        ↓
Playback in Web UI
```

## Project Structure

```text
empathy-engine/
├── app.py
├── emotion.py
├── emoji_utils.py
├── voice_mapper.py
├── tts_engine.py
├── static/
│   └── output.wav
├── templates/
│   └── index.html
├── requirements.txt
└── README.md
```

## Modules

### `emotion.py`

- Uses the Hugging Face model `j-hartmann/emotion-english-distilroberta-base`.
- Detects the dominant emotion from text using `transformers.pipeline`.
- Normalizes labels into `joy`, `sadness`, `anger`, or `neutral`.
- Defaults to a rule-based fallback for demo reliability.
- Loads the Hugging Face model only when `EMPATHY_USE_HF_MODEL=1` is set.

Example output:

```python
{"emotion": "joy", "confidence": 0.91}
```

### `emoji_utils.py`

- Extracts emojis from input text.
- Maps them into emotional signals or intensity boosters.
- Adjusts the final intensity and can override the model emotion when emoji evidence is stronger.

Example output:

```python
{"emotion": "joy", "intensity": 1.2}
```

### `voice_mapper.py`

- Converts emotion and intensity into voice settings.
- Controls speaking rate and volume as a lightweight proxy for prosody.

Illustrative behavior:

- `joy`: faster and fuller delivery
- `sadness`: slower and softer delivery
- `anger`: faster and louder delivery
- `neutral`: balanced defaults

### `tts_engine.py`

- Uses `pyttsx3` for offline text-to-speech.
- Applies the mapped rate and volume.
- Saves generated speech to `static/output.wav`.

### `app.py`

- Serves the Flask web app.
- Handles the end-to-end pipeline:

```text
User Input
→ detect_emotion()
→ boost_emotion_with_emojis()
→ map_emotion_to_voice()
→ generate_audio()
→ render output
```

### `templates/index.html`

- Provides a web form for entering text.
- Plays the generated WAV file in-browser.
- Displays a lightweight debug panel with emotion, confidence, intensity, and voice settings.

## Design Decisions

### Why not API TTS?

- Offline reliability
- No dependency on external service uptime
- No additional request latency

### Why emoji integration?

- Emojis act as explicit emotional signals in modern text
- They can correct or amplify weak model signals
- They make the emotional interpretation more context-aware

### Why rule-based mapping?

- Simpler and explainable
- Easy to tune during demos and interviews
- A practical way to mimic prosodic shifts without a full neural TTS stack

## Bonus Features

- Emotion debug panel in the UI
- The code structure supports adding multiple voice styles later
- The pipeline can be extended toward SSML-aware synthesis in a future version

## Limitations

- `pyttsx3` offers limited pitch control
- The system is rule-based rather than a deep-learning expressive TTS model
- Emoji interpretation is heuristic and not culturally exhaustive
- First model load may require internet access to download Hugging Face weights

## Run

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

### Optional: enable the Hugging Face model

By default, the app uses the offline fallback detector so the demo starts instantly.

If you want to enable the transformer model, set this environment variable before running:

```bash
EMPATHY_USE_HF_MODEL=1
```

On Windows PowerShell:

```powershell
$env:EMPATHY_USE_HF_MODEL="1"
python app.py
```

## Interview Summary

> This system bridges NLP-based emotion detection with speech synthesis by dynamically modulating prosodic features like rate and volume, enhanced with emoji-based contextual understanding.
