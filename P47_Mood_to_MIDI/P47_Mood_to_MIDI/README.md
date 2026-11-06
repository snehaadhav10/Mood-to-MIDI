# P47 – Mood-to-MIDI with MuseGAN

A Streamlit academic prototype that maps a natural-language mood sentence to a musical arrangement, samples multiple random seeds, exports MIDI/WAV, and optionally evaluates text-audio similarity with LAION-CLAP.

## Important implementation note

The app has two generation paths:

1. **MuseGAN adapter:** consumes a `.npz` multitrack pianoroll produced by the official pretrained MuseGAN inference workflow. Set `MUSEGAN_SAMPLE_NPZ` to that file. The official repository is an older research codebase; its model environment/checkpoints must be installed separately.
2. **Demo fallback:** if no MuseGAN sample is configured, it creates a procedural multi-track MIDI so the interface and export workflow can be demonstrated. The app labels this honestly; it is not MuseGAN output.

The demo fallback is not a substitute for the pretrained MuseGAN deliverable.

## Setup (Windows + VS Code)

Use Python 3.10 for the most compatible research environment.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Copy `.env.example` to `.env` and add your Gemini API key if you want LLM-based mood mapping. Without it, a local rule-based mood mapper keeps the app usable.

Run:
```powershell
streamlit run app.py
```

## Connect pretrained MuseGAN

1. Clone the original research repository: https://github.com/salu133445/musegan
2. Follow its README to download pretrained models and run its inference script.
3. The inference workflow saves multitrack pianoroll `.npz` output.
4. Set `MUSEGAN_SAMPLE_NPZ` in `.env` to the full path of a generated `.npz` file.
5. Restart Streamlit.

The adapter currently reads a generated pianoroll sample. To make every random seed run a fresh MuseGAN inference, connect the official inference script in `src/generator.py` for the exact version/checkpoint installed in your environment. Do not claim fresh MuseGAN sampling until that integration is completed.

Official MuseGAN documentation describes five tracks (bass, drums, guitar, piano, strings), pretrained inference, and `.npz` to MIDI export: https://github.com/salu133445/musegan

## CLAP evaluation

Enable “Evaluate mood with CLAP” in the sidebar. CLAP setup may require a compatible PyTorch/TorchAudio installation and a downloaded checkpoint. For music-specific evaluation, LAION publishes music-trained checkpoints; see https://github.com/LAION-AI/CLAP and https://huggingface.co/laion/larger_clap_music.

A CLAP similarity score is not a copyright detector or an objective measure of musical quality.

## Three demonstration moods

Try these prompts:
- **Happy:** “Create cheerful, upbeat music for a sunny celebration.”
- **Sad:** “Generate a slow, emotional and melancholic piano piece.”
- **Calm:** “Make peaceful, relaxing music for meditation.”

Generate at least three variations for each mood. Save one MIDI and WAV clip per mood for the project demonstration.

## Deliverables checklist

- [x] Streamlit music app interface
- [x] Natural-language mood input
- [x] Mood-to-tempo / instrument mapping (LLM optional, local fallback included)
- [x] Multiple latent-seed-style variation runs
- [x] MIDI and WAV export
- [x] Originality and copyright notice
- [ ] Connect and verify pretrained MuseGAN inference with checkpoint
- [ ] Configure and verify CLAP checkpoint on generated audio
- [ ] Record three final clips (happy, sad, calm) using the pretrained MuseGAN path

## Suggested project structure

```text
P47_Mood_to_MIDI/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── mood_engine.py
│   ├── generator.py
│   ├── evaluator.py
│   ├── exporter.py
│   └── notes.py
└── outputs/
```
