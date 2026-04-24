# pages/_Research_Pod.py
"""
Module 5.2 – Research Pod (Conversational Audio Module)
Generates a two-person academic podcast dialogue from a paper, then
converts it to audio using gTTS.
"""

from utils.ui_components import load_css
import streamlit as st
import base64
import re
from utils.api import call_api
from utils.pdf_utils import extract_text_from_pdf

st.title("🎙️ Research Pod")
load_css("assets/styles.css")
st.markdown(
    "Transform any research paper into an engaging **two-person academic podcast**."
)

# ── Podcast Settings ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎙️ Podcast Personas")
    host_name = st.text_input("Host Name", value="Jamie", help="The enthusiastic interviewer")
    expert_name = st.text_input("Expert Name", value="Dr. Aisha", help="The academic researcher")
    
    st.markdown("---")
    st.markdown("### 🎭 Deep Realism Settings")
    
    voice_vibe = st.selectbox(
        "Voice Duo / Vibe",
        options=["Standard Academic (US)", "Oxford Scholars (UK)", "Modern Dialogue (US)"],
        index=0
    )
    
    base_speed = st.slider("Speech Speed", 0.5, 1.5, 0.9, 0.05)
    dramatic_pauses = st.checkbox("Enable Dramatic Pauses", value=True, help="Adds 'thinking' gaps and natural breaks.")
    
    st.markdown("---")
    st.info("The AI will use these names for the dialogue and voice assignment.")

st.markdown("---")

# ── Paper Source Selector ──────────────────────────────────────────────────────
st.markdown('<div class="vision-panel">', unsafe_allow_html=True)
source_mode = st.radio(
    "🎯 Select Paper Source for Podcast",
    ["Use Main Session Paper", "Upload New Paper for this Pod"],
    horizontal=True,
    help="Choose whether to use the paper from your main session or upload a different one."
)

paper_text = None
paper_name = None

if source_mode == "Use Main Session Paper":
    if st.session_state.get("paper_text"):
        paper_text = st.session_state.paper_text
        paper_name = st.session_state.get("paper_name", "Session Paper")
        st.success(f"🔗 Linked to main paper: **{paper_name}**")
    else:
        st.warning("⚠️ No paper found in main session. Please upload one below.")
        uploaded = st.file_uploader("📄 Upload Paper", type=["pdf"], key="pod_fallback_upload")
        if uploaded:
            with st.spinner("Extracting text..."):
                paper_text = extract_text_from_pdf(uploaded)
                paper_name = uploaded.name
else:
    uploaded = st.file_uploader("📄 Upload Specific Paper for Pod", type=["pdf"], key="pod_fresh_upload")
    if uploaded:
        with st.spinner("Extracting text..."):
            paper_text = extract_text_from_pdf(uploaded)
            paper_name = uploaded.name
        st.success(f"✅ Loaded specific paper: **{paper_name}**")

st.markdown('</div>', unsafe_allow_html=True)

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
        # Handle emotional tags for display
        display_line = line
        if line.startswith(f"{host_name}:"):
            content = line[len(host_name)+1:].strip()
            # Wrap [Emotion] in italics
            content = re.sub(r'(\[[A-Za-z]+\])', r'<i style="opacity: 0.7; font-size: 0.9em;">\1</i>', content)
            
            st.markdown(
                f"<div style='background:#1e3a5f;color:#d6eaff;padding:8px 14px;"
                f"border-radius:8px;margin-bottom:6px;'>"
                f"🎤 <strong>{host_name}:</strong> {content}</div>",
                unsafe_allow_html=True,
            )
        elif line.startswith(f"{expert_name}:"):
            content = line[len(expert_name)+1:].strip()
            # Wrap [Emotion] in italics
            content = re.sub(r'(\[[A-Za-z]+\])', r'<i style="opacity: 0.7; font-size: 0.9em;">\1</i>', content)
            
            st.markdown(
                f"<div style='background:#1a3d2b;color:#c8f5dc;padding:8px 14px;"
                f"border-radius:8px;margin-bottom:6px;'>"
                f"🎓 <strong>{expert_name}:</strong> {content}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(line)

    # ── Audio Generation ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔊 Generate Audio")
    st.info(
        "Generate high-quality **multi-voice audio** using artificial intelligence."
    )

    if st.button("🎧 Generate Podcast Audio", key="pod_audio"):
        with st.spinner("Generating multi-voice audio with 'Deep Realism'..."):
            tts_result = call_api("/podcast-audio", {
                "script": script,
                "host_name": host_name,
                "expert_name": expert_name,
                "vibe": voice_vibe,
                "speed": base_speed,
                "dramatic_pauses": dramatic_pauses
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
