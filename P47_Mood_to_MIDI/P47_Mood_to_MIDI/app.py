import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from src.mood_engine import analyze_mood
from src.generator import generate_candidates
from src.evaluator import score_with_clap
from src.exporter import save_midi, render_audio
from src.notes import COPYRIGHT_NOTE

st.set_page_config(page_title="Mood-to-MIDI | MuseGAN", page_icon="🎹", layout="wide")
st.title("🎹 Mood-to-MIDI with MuseGAN")
st.caption("Turn a sentence about a feeling into a multi-track musical idea.")

with st.sidebar:
    st.header("Generation settings")
    candidates = st.slider("Latent seed variations", 1, 8, 3)
    bars = st.selectbox("Length", [4, 8, 16], index=1)
    use_clap = st.checkbox("Evaluate mood with CLAP (optional)", value=False)
    st.divider()
    st.caption("MuseGAN mode is enabled when a generated .npz sample is supplied in the project configuration. Otherwise, the app uses a clearly labelled MIDI demo fallback.")

mood_text = st.text_area(
    "Describe the mood of your music",
    placeholder="Example: Create calm, warm music for a quiet rainy evening.",
    height=100
)
generate = st.button("✨ Generate music", type="primary", use_container_width=True)

if generate:
    if not mood_text.strip():
        st.warning("Please enter a mood sentence first.")
        st.stop()

    with st.spinner("Understanding the mood and generating musical variations..."):
        profile = analyze_mood(mood_text)
        results = generate_candidates(profile, n=candidates, bars=bars)

    st.subheader("1. Mood interpretation")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Detected mood", profile["mood"].title())
    c2.metric("Suggested tempo", f'{profile["tempo"]} BPM')
    c3.metric("Key", profile["key"])
    c4.metric("Tracks", len(profile["tracks"]))

    st.write("**Arrangement:** " + ", ".join(profile["tracks"]))
    st.write("**Musical direction:** " + profile["description"])

    st.subheader("2. Generated variations")
    scored = []
    for item in results:
        score = None
        if use_clap:
            score = score_with_clap(item["wav_path"], mood_text)
        item["clap_score"] = score
        scored.append(item)

    # When CLAP is enabled, use its score to select the best candidate.
    if use_clap and any(x["clap_score"] is not None for x in scored):
        scored.sort(key=lambda x: x["clap_score"] or -1, reverse=True)

    for idx, item in enumerate(scored, start=1):
        with st.expander(f'Variation {idx} · seed {item["seed"]}' + (f' · CLAP {item["clap_score"]:.3f}' if item["clap_score"] is not None else ""), expanded=(idx == 1)):
            st.caption(item["engine"])
            audio_bytes = Path(item["wav_path"]).read_bytes()
            st.audio(audio_bytes, format="audio/wav")
            st.download_button("Download MIDI", Path(item["midi_path"]).read_bytes(),
                               file_name=f'mood_music_seed_{item["seed"]}.mid',
                               mime="audio/midi", key=f"midi_{idx}")
            st.download_button("Download WAV", audio_bytes,
                               file_name=f'mood_music_seed_{item["seed"]}.wav',
                               mime="audio/wav", key=f"wav_{idx}")

    st.subheader("3. Originality and copyright")
    st.info(COPYRIGHT_NOTE)
    st.caption("CLAP similarity is an approximate text-audio alignment score, not a legal originality or copyright test.")

st.divider()
st.caption("Academic prototype · MuseGAN is a research model for multi-track symbolic music generation.")
