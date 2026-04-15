from __future__ import annotations

import asyncio
from pathlib import Path

import pyttsx3


def _generate_with_pyttsx3(text: str, rate: int, volume: float, output_path: Path) -> dict[str, str]:
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.save_to_file(text, str(output_path))
    engine.runAndWait()
    engine.stop()
    return {
        "backend": "pyttsx3",
        "mime_type": "audio/wav",
    }


async def _edge_tts_bytes(
    *,
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> bytes:
    import edge_tts

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    chunks: list[bytes] = []
    async for item in communicate.stream():
        if item["type"] == "audio":
            chunks.append(item["data"])
    return b"".join(chunks)


async def _generate_with_edge_tts(
    *,
    text: str,
    output_path: Path,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> dict[str, str]:
    audio_bytes = await _edge_tts_bytes(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    output_path.write_bytes(audio_bytes)
    return {
        "backend": "edge-tts",
        "mime_type": "audio/mpeg",
    }


async def _generate_segmented_edge_tts(
    *,
    segments: list[dict[str, str]],
    output_path: Path,
) -> dict[str, str]:
    combined = bytearray()
    for segment in segments:
        text = segment["text"].strip()
        if not text:
            continue
        audio_bytes = await _edge_tts_bytes(
            text=text,
            voice=segment["voice"],
            rate=segment["rate"],
            volume=segment["volume"],
            pitch=segment["pitch"],
        )
        combined.extend(audio_bytes)

    output_path.write_bytes(bytes(combined))
    return {
        "backend": "edge-tts-segmented",
        "mime_type": "audio/mpeg",
    }


def generate_audio(
    *,
    text: str,
    rate: int,
    volume: float,
    output_path: str | Path,
    edge_voice: str | None = None,
    edge_rate: str = "+0%",
    edge_volume: str = "+0%",
    edge_pitch: str = "+0Hz",
) -> dict[str, str]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() == ".mp3" and edge_voice:
        try:
            return asyncio.run(
                _generate_with_edge_tts(
                    text=text,
                    output_path=path,
                    voice=edge_voice,
                    rate=edge_rate,
                    volume=edge_volume,
                    pitch=edge_pitch,
                )
            )
        except Exception:
            # Fall back to the local offline engine if the online backend is unavailable.
            wav_path = path.with_suffix(".wav")
            result = _generate_with_pyttsx3(text, rate, volume, wav_path)
            result["fallback_path"] = wav_path.name
            return result

    return _generate_with_pyttsx3(text, rate, volume, path)


def generate_segmented_audio(
    *,
    segments: list[dict[str, str]],
    output_path: str | Path,
    fallback_rate: int,
    fallback_volume: float,
) -> dict[str, str]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.suffix.lower() == ".mp3" and segments:
        try:
            return asyncio.run(
                _generate_segmented_edge_tts(
                    segments=segments,
                    output_path=path,
                )
            )
        except Exception:
            wav_path = path.with_suffix(".wav")
            combined_text = " ".join(segment["text"] for segment in segments if segment["text"].strip())
            result = _generate_with_pyttsx3(combined_text, fallback_rate, fallback_volume, wav_path)
            result["fallback_path"] = wav_path.name
            return result

    combined_text = " ".join(segment["text"] for segment in segments if segment["text"].strip())
    return _generate_with_pyttsx3(combined_text, fallback_rate, fallback_volume, path)
