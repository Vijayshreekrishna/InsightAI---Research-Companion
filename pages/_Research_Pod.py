# pages/_Research_Pod.py
"""
Module 5.2 – Research Pod (Conversational Audio Module)
Generates a two-person academic podcast dialogue from a paper, then
converts it to audio using gTTS.
"""

import streamlit as st
import base64
from utils.api import call_api
from utils.pdf_utils import extract_text_from_pdf

st.title("🎙️ Research Pod")
st.markdown(
    "Transform any research paper into an engaging **two-person academic podcast** "
    "between *Dr. Aisha (Expert)* and *Jamie (Host)*."
)

st.markdown("---")

# ── Paper Source ──────────────────────────────────────────────────────────────
paper_text = None
paper_name = None

if st.session_state.get("paper_text"):
    st.success(
        f"✅ Using paper already loaded: **{st.session_state.get('paper_name', 'Uploaded Paper')}**"
    )
    use_existing = st.checkbox("Use this paper for the podcast", value=True)
    if use_existing:
        paper_text = st.session_state.paper_text
        paper_name = st.session_state.get("paper_name", "paper.pdf")

if not paper_text:
    uploaded = st.file_uploader(
        "📄 Upload a Research Paper (or use the one already loaded above)",
        type=["pdf"],
        key="pod_upload"
    )
    if uploaded:
        with st.spinner("Reading paper..."):
            paper_text = extract_text_from_pdf(uploaded)
        paper_name = uploaded.name
        st.success(f"✅ Loaded **{paper_name}**")

# ── Generate Podcast Script ────────────────────────────────────────────────────
if paper_text:
    if st.button("🎬 Generate Podcast Script", key="pod_generate"):
        with st.spinner("Writing podcast dialogue... (this may take 20–40 seconds)"):
            result = call_api("/podcast-script", {"text": paper_text})
        if "script" in result:
            st.session_state["podcast_script"] = result["script"]
            st.session_state["podcast_paper_name"] = paper_name
        else:
            st.error(result.get("error", "Script generation failed."))

# ── Display Script ─────────────────────────────────────────────────────────────
if st.session_state.get("podcast_script"):
    script = st.session_state["podcast_script"]
    st.markdown("---")
    st.markdown("#### 📜 Podcast Script")

    # Colour-coded rendering
    for line in script.strip().split("\n"):
        line = line.strip()
        if not line:
            st.markdown("")
            continue
        if line.startswith("Jamie:"):
            st.markdown(
                f"<div style='background:#1e3a5f;color:#d6eaff;padding:8px 14px;"
                f"border-radius:8px;margin-bottom:6px;'>"
                f"🎤 <strong>Jamie:</strong> {line[6:].strip()}</div>",
                unsafe_allow_html=True,
            )
        elif line.startswith("Dr. Aisha:"):
            st.markdown(
                f"<div style='background:#1a3d2b;color:#c8f5dc;padding:8px 14px;"
                f"border-radius:8px;margin-bottom:6px;'>"
                f"🎓 <strong>Dr. Aisha:</strong> {line[10:].strip()}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(line)

    # ── Audio Generation ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔊 Generate Audio")
    st.info(
        "Audio is generated as a single voice (gTTS). For best results, the script "
        "is read sequentially with speaker labels included."
    )

    if st.button("🎧 Generate Podcast Audio", key="pod_audio"):
        # Prepare a clean version with speaker labels pronounced naturally
        clean_lines = []
        for line in script.strip().split("\n"):
            line = line.strip()
            if line.startswith("Jamie:"):
                clean_lines.append("Jamie says: " + line[6:].strip())
            elif line.startswith("Dr. Aisha:"):
                clean_lines.append("Doctor Aisha says: " + line[10:].strip())
            elif line:
                clean_lines.append(line)

        tts_text = "\n\n".join(clean_lines)

        with st.spinner("Generating audio... (this takes a moment)"):
            tts_result = call_api("/tts", {"text": tts_text[:4500]})

        if tts_result.get("audio_base64"):
            audio_bytes = base64.b64decode(tts_result["audio_base64"])
            st.audio(audio_bytes, format="audio/mp3")
            st.success("🎧 Podcast audio ready! Press play above.")
            st.download_button(
                "⬇️ Download Audio",
                data=audio_bytes,
                file_name="research_pod.mp3",
                mime="audio/mp3"
            )
        else:
            st.error(tts_result.get("error", "Audio generation failed."))

else:
    st.info("Upload a paper or go to **Smart Summary** first to load one.")
