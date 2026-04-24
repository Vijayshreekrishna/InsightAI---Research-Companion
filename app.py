# app.py
import streamlit as st
from utils.ui_components import load_css, title_banner
from utils.pdf_utils import extract_text_from_pdf
from utils.api import call_api
import io

# Page configuration
st.set_page_config(
    page_title="Insight-AI | The Last Research Tool You'll Ever Need",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_css("assets/styles.css")

# Sidebar
with st.sidebar:
    st.markdown("### 🗂️ Active Command Centers")
    st.markdown("- 🧠 **The Synthesizer** (Summary/Compare)")
    st.markdown("- 👁️ **The Oracle** (Chat/Visual Q&A)")
    st.markdown("- 📢 **The Broadcaster** (Audio/Drafting)")
    st.divider()
    if st.button("🔁 Clear Neural Cache", use_container_width=True):
        st.session_state.messages = []
        st.toast("System cache cleared.")

# --- HERO SECTION ---
st.markdown("""
<div class="hero-section">
    <div class="hero-title">INSIGHT-AI</div>
    <div style="font-size: 1.3rem; color: #94a3b8; font-weight: 500;">
        Welcome to <strong>Insight-AI</strong> 👋 — head to the tabs to begin.
    </div>
</div>
""", unsafe_allow_html=True)

# --- NARRATIVE PANELS ---

# 1. THE SYNTHESIZER
st.markdown("""
<div class="vision-panel">
    <div class="panel-header">
        <div class="panel-icon">🧠</div>
        <div>
            <div class="panel-title">The Synthesizer</div>
        </div>
    </div>
    <p style="color:#94a3b8; font-size:1.1rem; margin-bottom:20px;">
        Transform massive PDFs into high-density insights. Our synthesis engine extracts methodology, datasets, and future work in seconds.
    </p>
    <div class="feature-pill-grid">
        <div class="feature-pill">🧱 Smart Summary</div>
        <div class="feature-pill">📊 Compare Two Papers</div>
        <div class="feature-pill">💡 Future Directions</div>
        <div class="feature-pill">📚 Semantic Library</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. THE ORACLE
st.markdown("""
<div class="vision-panel">
    <div class="panel-header">
        <div class="panel-icon">👁️</div>
        <div>
            <div class="panel-title">The Oracle</div>
        </div>
    </div>
    <p style="color:#94a3b8; font-size:1.1rem; margin-bottom:20px;">
        Interrogate the document. Ask complex questions, map citation networks, and perform visual Q&A on charts and tables.
    </p>
    <div class="feature-pill-grid">
        <div class="feature-pill">💬 Deep Chat (True RAG)</div>
        <div class="feature-pill">🔬 Visual PDF Interrogation</div>
        <div class="feature-pill">🕸️ Citation Graph Mapping</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. THE BROADCASTER
st.markdown("""
<div class="vision-panel">
    <div class="panel-header">
        <div class="panel-icon">📢</div>
        <div>
            <div class="panel-title">The Broadcaster</div>
        </div>
    </div>
    <p style="color:#94a3b8; font-size:1.1rem; margin-bottom:20px;">
        Turn your research into its final form. Automatically generate professional podcasts or format your messy notes into academic drafts.
    </p>
    <div class="feature-pill-grid">
        <div class="feature-pill">🎙️ Two-Person Research Pod</div>
        <div class="feature-pill">📝 Paper Formatter (IEEE/ACM)</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="protocol-banner">
    <h3 style="color:#ffffff; margin-bottom:10px;">🛡️ The InsightAI Protocol</h3>
    <div style="display:flex; justify-content:center; gap:30px; color:#94a3b8;">
        <span>✅ No Hallucinations</span>
        <span>✅ Page-Verified Citations</span>
        <span>✅ Mechanical Fidelity</span>
    </div>
</div>
""", unsafe_allow_html=True)
