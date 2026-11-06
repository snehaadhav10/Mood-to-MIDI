"""Candidate generation. Uses an imported MuseGAN pianoroll when configured; otherwise creates a transparent demo MIDI."""
import os, random, tempfile
from pathlib import Path
import numpy as np
from src.exporter import midi_from_demo

def _try_musegan(profile, seed, bars):
    sample_path = os.getenv("MUSEGAN_SAMPLE_NPZ")
    if not sample_path or not Path(sample_path).exists():
        return None
    try:
        import pypianoroll
        from pypianoroll import Multitrack
        from src.exporter import convert_pianoroll_to_midi
        # The official MuseGAN inference script writes pianoroll .npz samples.
        # This adapter consumes a generated sample; it does not pretend to run training.
        roll = Multitrack(sample_path)
        out = Path("outputs") / f"musegan_seed_{seed}.mid"
        convert_pianoroll_to_midi(roll, out, profile)
        return str(out)
    except Exception:
        return None

def generate_candidates(profile, n=3, bars=8):
    Path("outputs").mkdir(exist_ok=True)
    results = []
    for i in range(n):
        seed = random.randint(1, 2**31 - 1)
        random.seed(seed)
        np.random.seed(seed % (2**32 - 1))
        midi_path = _try_musegan(profile, seed, bars)
        engine = "Pretrained MuseGAN pianoroll adapter" if midi_path else "Demo fallback (procedural MIDI; MuseGAN checkpoint not connected)"
        if midi_path is None:
            midi_path = str(Path("outputs") / f"demo_seed_{seed}.mid")
            midi_from_demo(profile, seed, bars, midi_path)
        from src.exporter import render_audio
        wav_path = str(Path("outputs") / f"audio_seed_{seed}.wav")
        render_audio(midi_path, wav_path)
        results.append({"seed": seed, "midi_path": midi_path, "wav_path": wav_path, "engine": engine})
    return results
