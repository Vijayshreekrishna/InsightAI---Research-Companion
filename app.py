# app.py
import streamlit as st
from utils.ui_components import load_css, title_banner
from utils.pdf_utils import extract_text_from_pdf
from utils.api import call_api
import io

# Page configuration
st.set_page_config(
    page_title="Insight-AI - Your AI Research Companion",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_css("assets/styles.css")

# Title Banner
title_banner()

# Sidebar
st.sidebar.title("Insight-AI")
st.sidebar.caption("Your AI Research Companion")

if st.sidebar.button("🔁 Reset Chat"):
    st.session_state.messages = []
    st.toast("Chat reset", icon="✅")

st.sidebar.markdown("---")
st.sidebar.markdown("**📖 Core Features**")
st.sidebar.markdown("- 🧱 **Smart Summary** — Summarize & extract insights")
st.sidebar.markdown("- 💬 **Chat with Paper** — Q&A with RAG history")
st.sidebar.markdown("- 📊 **Compare Two Papers** — Side-by-side analysis")
st.sidebar.markdown("- 💡 **Insights & Future Work** — Trends & directions")
st.sidebar.markdown("---")
st.sidebar.markdown("**🆕 Advanced Modules**")
st.sidebar.markdown("- 🔬 **Visual Q&A** — Interrogate specific PDF pages")
st.sidebar.markdown("- 🎙️ **Research Pod** — Podcast-style audio summaries")
st.sidebar.markdown("- 📚 **Local Insights** — Semantic RAG library")
st.sidebar.markdown("- 🕸️ **Citation Graph** — Citation influence network")
st.sidebar.markdown("---")


st.markdown("Welcome to **Insight-AI** 👋 — head to the tabs to begin.")

st.markdown("""
<div class="info-banner">
    <h3>ℹ️ About & Verification Rules</h3>
    <p>Insight-AI is your research companion. We <strong>summarize</strong>, <strong>chat</strong>, and <strong>discover</strong> insights.</p>
    <hr>
    <ul>
        <li><strong>No Hallucinations:</strong> Strictly grounded in provided PDF.</li>
        <li><strong>Citations:</strong> All claims backed by page references (e.g. <code>[Page 3]</code>).</li>
        <li><strong>Transparency:</strong> We tell you if the info isn't there.</li>
        <li><strong>RAG Memory:</strong> Chat with Paper automatically searches your historical library.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
