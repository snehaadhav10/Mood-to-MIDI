
"""Mood-to-music mapping using Gemini or a local fallback."""

import os
import json
import re

ALLOWED_TRACKS = ["Drums", "Bass", "Guitar", "Piano", "Strings"]

MOOD_PROFILES = {
    "sad": {
        "tempo": 72,
        "key": "A minor",
        "tracks": ["Piano", "Strings", "Bass"],
        "description": "Slow melodies, gentle dynamics and emotional minor-key harmonies."
    },
    "happy": {
        "tempo": 118,
        "key": "C major",
        "tracks": ["Drums", "Bass", "Guitar", "Piano"],
        "description": "Bright melodies, energetic rhythms and cheerful major-key harmony."
    },
    "calm": {
        "tempo": 78,
        "key": "G major",
        "tracks": ["Piano", "Strings", "Bass"],
        "description": "Gentle melodies, spacious phrasing and warm relaxing harmonies."
    },
    "intense": {
        "tempo": 132,
        "key": "D minor",
        "tracks": ["Drums", "Bass", "Guitar", "Strings"],
        "description": "Powerful rhythms, strong bass and dramatic musical movement."
    },
    "romantic": {
        "tempo": 82,
        "key": "A minor",
        "tracks": ["Piano", "Strings", "Bass"],
        "description": "Soft expressive melodies with warm and emotional harmonies."
    },
    "dreamy": {
        "tempo": 85,
        "key": "G major",
        "tracks": ["Piano", "Strings"],
        "description": "Floating melodies, soft textures and spacious atmospheric harmony."
    },
    "nostalgic": {
        "tempo": 88,
        "key": "A minor",
        "tracks": ["Piano", "Strings", "Guitar"],
        "description": "Reflective melodies with warm, sentimental musical textures."
    },
    "focused": {
        "tempo": 100,
        "key": "C major",
        "tracks": ["Piano", "Bass"],
        "description": "Steady rhythms and simple, balanced melodies for concentration."
    },
    "hopeful": {
        "tempo": 100,
        "key": "C major",
        "tracks": ["Drums", "Bass", "Piano", "Strings"],
        "description": "Balanced rhythms and uplifting, optimistic harmonies."
    }
}

MOOD_KEYWORDS = {
    "sad": ["sad", "melancholy", "lonely", "grief", "heartbreak", "crying"],
    "happy": ["happy", "joy", "cheerful", "upbeat", "excited", "fun"],
    "calm": ["calm", "peace", "relax", "meditat", "gentle", "rainy", "peaceful"],
    "intense": ["angry", "intense", "powerful", "epic", "dramatic", "aggressive"],
    "romantic": ["romantic", "love", "affection", "passionate"],
    "dreamy": ["dreamy", "magical", "floating", "ethereal", "fantasy"],
    "nostalgic": ["nostalgic", "memories", "childhood", "reminiscent"],
    "focused": ["focused", "study", "concentration", "productive", "working"],
    "hopeful": ["hopeful", "inspiring", "motivational", "optimistic"]
}


def _fallback(text: str) -> dict:
    """Detect mood using local keywords without an API."""

    t = text.lower()

    detected_mood = "hopeful"

    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in t for keyword in keywords):
            detected_mood = mood
            break

    profile = MOOD_PROFILES[detected_mood].copy()

    return {
        "mood": detected_mood,
        "tempo": profile["tempo"],
        "key": profile["key"],
        "tracks": profile["tracks"],
        "description": profile["description"],
        "prompt": text
    }


def _clean_response(data: dict, original_text: str) -> dict:
    """Validate and normalize Gemini output."""

    mood = str(data.get("mood", "hopeful")).lower().strip()

    if mood not in MOOD_PROFILES:
        mood = "hopeful"

    defaults = MOOD_PROFILES[mood]

    try:
        tempo = int(data.get("tempo", defaults["tempo"]))
    except (TypeError, ValueError):
        tempo = defaults["tempo"]

    tempo = max(55, min(160, tempo))

    key = str(data.get("key", defaults["key"])).strip()
    if not key or len(key) > 30:
        key = defaults["key"]

    raw_tracks = data.get("tracks", defaults["tracks"])

    if not isinstance(raw_tracks, list):
        raw_tracks = defaults["tracks"]

    tracks = [
        track for track in raw_tracks
        if isinstance(track, str) and track in ALLOWED_TRACKS
    ]

    if not tracks:
        tracks = defaults["tracks"]

    description = str(
        data.get("description", defaults["description"])
    ).strip()

    if not description:
        description = defaults["description"]

    return {
        "mood": mood,
        "tempo": tempo,
        "key": key,
        "tracks": tracks,
        "description": description,
        "prompt": original_text
    }


def analyze_mood(text: str) -> dict:
    """Analyze a mood using Gemini or the local fallback."""

    if not text or not text.strip():
        return _fallback("hopeful")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return _fallback(text)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = f"""
Analyze the following music request.

Choose one mood from:
{list(MOOD_PROFILES.keys())}

Return ONLY valid JSON with these keys:
- mood: short mood label
- tempo: integer between 55 and 160
- key: musical key such as C major or A minor
- tracks: list containing only {ALLOWED_TRACKS}
- description: one sentence describing the musical direction

User request: {text}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = response.text or ""

        raw = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw.strip(),
            flags=re.IGNORECASE
        )

        data = json.loads(raw)

        if not isinstance(data, dict):
            raise ValueError("Gemini returned an invalid response.")

        return _clean_response(data, text)

    except Exception:
        # Keep the app working even if Gemini is unavailable.
        return _fallback(text)
