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
    "Transform any research paper into an engaging **two-person academic podcast**."
)

# ── Podcast Settings ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎙️ Podcast Personas")
    host_name = st.text_input("Host Name", value="Jamie", help="The enthusiastic interviewer")
    expert_name = st.text_input("Expert Name", value="Dr. Aisha", help="The academic researcher")
    
    st.markdown("---")
    st.info("The AI will use these names for the dialogue and voice assignment.")

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
        with st.spinner(f"Writing podcast dialogue for {host_name} and {expert_name}..."):
            result = call_api("/podcast-script", {
                "text": paper_text,
                "host_name": host_name,
                "expert_name": expert_name
            })
        if "script" in result:
            st.session_state["podcast_script"] = result["script"]
            st.session_state["podcast_paper_name"] = paper_name
            st.session_state["pod_host"] = host_name
            st.session_state["pod_expert"] = expert_name
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
        if line.startswith(f"{host_name}:"):
            st.markdown(
                f"<div style='background:#1e3a5f;color:#d6eaff;padding:8px 14px;"
                f"border-radius:8px;margin-bottom:6px;'>"
                f"🎤 <strong>{host_name}:</strong> {line[len(host_name)+1:].strip()}</div>",
                unsafe_allow_html=True,
            )
        elif line.startswith(f"{expert_name}:"):
            st.markdown(
                f"<div style='background:#1a3d2b;color:#c8f5dc;padding:8px 14px;"
                f"border-radius:8px;margin-bottom:6px;'>"
                f"🎓 <strong>{expert_name}:</strong> {line[len(expert_name)+1:].strip()}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(line)

    # ── Audio Generation ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔊 Generate Audio")
    st.info(
        f"Generate high-quality **multi-voice audio** using artificial intelligence."
    )

    if st.button("🎧 Generate Podcast Audio", key="pod_audio"):
        with st.spinner("Generating multi-voice audio... (this may take a minute)"):
            tts_result = call_api("/podcast-audio", {
                "script": script,
                "host_name": host_name,
                "expert_name": expert_name
            })

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
