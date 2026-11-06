
"""Optional CLAP text-audio similarity evaluator."""

import streamlit as st


@st.cache_resource
def load_clap_model():
    import laion_clap

    # The default LAION checkpoint uses the HTSAT-tiny architecture.
    model = laion_clap.CLAP_Module(
        enable_fusion=False,
        amodel="HTSAT-tiny"
    )

    model.load_ckpt()
    return model


def score_with_clap(wav_path, text):
    try:
        import torch

        model = load_clap_model()

        audio_embed = model.get_audio_embedding_from_filelist(
            [wav_path],
            use_tensor=True
        )

        text_embed = model.get_text_embedding(
            [text],
            use_tensor=True
        )

        score = torch.nn.functional.cosine_similarity(
            audio_embed,
            text_embed,
            dim=1
        )

        return float(score.item())

    except Exception as error:
        print(f"CLAP evaluation error: {error}")
        return None
