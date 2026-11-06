
"""MIDI and WAV export utilities for Mood-to-MIDI."""

from pathlib import Path
import numpy as np
import pretty_midi
import wave

PROGRAMS = {
    "Piano": 0,
    "Guitar": 24,
    "Bass": 32,
    "Strings": 48,
    "Drums": 0
}

NOTE_NAMES = {
    "C": 0,
    "C#": 1, "DB": 1,
    "D": 2,
    "D#": 3, "EB": 3,
    "E": 4,
    "F": 5,
    "F#": 6, "GB": 6,
    "G": 7,
    "G#": 8, "AB": 8,
    "A": 9,
    "A#": 10, "BB": 10,
    "B": 11
}

MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


def _get_key_info(key):
    """Get the root pitch and scale for a musical key."""

    parts = str(key).strip().upper().split()

    root_name = parts[0] if parts else "C"
    mode = parts[1] if len(parts) > 1 else "MAJOR"

    root = 60 + NOTE_NAMES.get(root_name, 0)

    if mode == "MINOR":
        scale = MINOR_SCALE
    else:
        scale = MAJOR_SCALE

    return root, scale, mode


def _make_chord(root, scale, degree):
    """Create a three-note chord from a scale."""

    return [
        root + scale[degree % 7],
        root + scale[(degree + 2) % 7],
        root + scale[(degree + 4) % 7]
    ]


def midi_from_demo(profile, seed, bars, output_path):
    """Generate a key-aware multi-track MIDI composition."""

    rng = np.random.default_rng(seed)

    tempo = float(profile["tempo"])
    beat = 60.0 / tempo
    bars = int(bars)
    total_beats = bars * 4

    root, scale, mode = _get_key_info(profile["key"])

    pm = pretty_midi.PrettyMIDI(
        initial_tempo=tempo
    )

    if mode == "MINOR":
        progression = [0, 5, 3, 4]
    else:
        progression = [0, 4, 5, 3]

    tracks = profile.get(
        "tracks",
        ["Piano", "Bass", "Strings"]
    )

    for name in tracks:

        is_drum = name == "Drums"

        inst = pretty_midi.Instrument(
            program=0 if is_drum else PROGRAMS.get(name, 0),
            is_drum=is_drum,
            name=name
        )

        # DRUM TRACK
        if is_drum:

            for bar in range(bars):

                base = bar * 4

                pattern = [
                    (0, 36, 105),
                    (1, 42, 55),
                    (2, 38, 85),
                    (3, 42, 55)
                ]

                for offset, pitch, velocity in pattern:

                    start = (base + offset) * beat

                    inst.notes.append(
                        pretty_midi.Note(
                            velocity=velocity,
                            pitch=pitch,
                            start=start,
                            end=start + 0.10
                        )
                    )

        # MELODIC TRACKS
        else:

            for bar in range(bars):

                chord_degree = progression[
                    bar % len(progression)
                ]

                chord = _make_chord(
                    root,
                    scale,
                    chord_degree
                )

                start_beat = bar * 4
                start_time = start_beat * beat
                end_time = (start_beat + 4) * beat

                # PIANO
                if name == "Piano":

                    for chord_start in [0, 2]:

                        for pitch in chord:

                            start = (
                                start_beat + chord_start
                            ) * beat

                            inst.notes.append(
                                pretty_midi.Note(
                                    velocity=78,
                                    pitch=pitch,
                                    start=start,
                                    end=start + 1.5 * beat
                                )
                            )

                    # Add a simple melodic variation.
                    melody_degree = int(rng.integers(0, 7))
                    melody_pitch = root + scale[melody_degree] + 12

                    inst.notes.append(
                        pretty_midi.Note(
                            velocity=65,
                            pitch=melody_pitch,
                            start=(start_beat + 3) * beat,
                            end=(start_beat + 3.6) * beat
                        )
                    )

                # GUITAR
                elif name == "Guitar":

                    for chord_start in [0, 1, 2, 3]:

                        for pitch in chord:

                            start = (
                                start_beat + chord_start
                            ) * beat + 0.02

                            inst.notes.append(
                                pretty_midi.Note(
                                    velocity=65,
                                    pitch=pitch + 12,
                                    start=start,
                                    end=start + 0.65 * beat
                                )
                            )

                # BASS
                elif name == "Bass":

                    bass_pitch = chord[0] - 24

                    for offset in [0, 2]:

                        start = (
                            start_beat + offset
                        ) * beat

                        inst.notes.append(
                            pretty_midi.Note(
                                velocity=88,
                                pitch=bass_pitch,
                                start=start,
                                end=start + 1.5 * beat
                            )
                        )

                # STRINGS
                elif name == "Strings":

                    for pitch in chord:

                        inst.notes.append(
                            pretty_midi.Note(
                                velocity=58,
                                pitch=pitch + 12,
                                start=start_time,
                                end=end_time - 0.05
                            )
                        )

        pm.instruments.append(inst)

    output_path = str(output_path)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pm.write(output_path)

    return output_path


def convert_pianoroll_to_midi(multitrack, output_path, profile=None):
    """Convert a generated pianoroll into a MIDI file."""

    output_path = str(output_path)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if hasattr(multitrack, "write"):
        multitrack.write(output_path)
        return output_path

    raise TypeError(
        "The generated multitrack object cannot be exported as MIDI."
    )


def save_midi(multitrack, output_path, profile=None):
    """Save generated music as MIDI."""

    return convert_pianoroll_to_midi(
        multitrack,
        output_path,
        profile
    )


def render_audio(midi_path, wav_path):
    """Convert MIDI into WAV audio."""

    midi_path = str(midi_path)
    wav_path = str(wav_path)

    Path(wav_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pm = pretty_midi.PrettyMIDI(midi_path)

    sample_rate = 22050

    try:
        # Use FluidSynth when available.
        audio = pm.fluidsynth(
            fs=sample_rate
        )

    except Exception:
        # Fallback audio renderer.
        duration = max(
            1.0,
            pm.get_end_time()
        )

        audio = np.zeros(
            int(duration * sample_rate),
            dtype=np.float32
        )

        for inst in pm.instruments:

            for note in inst.notes:

                if inst.is_drum:
                    continue

                frequency = 440.0 * (
                    2 ** ((note.pitch - 69) / 12)
                )

                start = int(note.start * sample_rate)

                end = min(
                    len(audio),
                    int(note.end * sample_rate)
                )

                if end <= start:
                    continue

                x = np.arange(end - start) / sample_rate

                attack = np.minimum(1.0, x * 30)

                release = np.minimum(
                    1.0,
                    np.maximum(
                        0.0,
                        (note.end - note.start - x) * 20
                    )
                )

                envelope = attack * release

                tone = np.sin(
                    2 * np.pi * frequency * x
                )

                audio[start:end] += (
                    0.10
                    * note.velocity / 100
                    * envelope
                    * tone
                ).astype(np.float32)

        peak = (
            np.max(np.abs(audio))
            if len(audio)
            else 0
        )

        if peak > 0:
            audio = audio / peak * 0.8

    audio = np.asarray(audio, dtype=np.float32)

    audio = np.clip(
        audio,
        -1.0,
        1.0
    )

    pcm = (
        audio * 32767
    ).astype("<i2")

    with wave.open(wav_path, "wb") as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        wav_file.writeframes(
            pcm.tobytes()
        )

    return wav_path
