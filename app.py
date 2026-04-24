# app.py
import streamlit as st
from utils.ui_components import load_css, title_banner
from utils.key_storage import load_user_keys, save_user_keys
from utils.pdf_utils import extract_text_from_pdf
from utils.api import call_api
import io

# Initialize persistent keys on first load
if "keys_initialized" not in st.session_state:
    saved_keys = load_user_keys()
    st.session_state.user_groq_key = saved_keys.get("groq", "")
    st.session_state.user_gemini_key = saved_keys.get("gemini", "")
    st.session_state.user_openai_key = saved_keys.get("openai", "")
    st.session_state.user_hf_key = saved_keys.get("hf", "")
    st.session_state.keys_initialized = True

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
    st.markdown("### 🧠 Neural Configuration")
    
    selected_model = st.selectbox(
        "Select AI Brain",
        options=["Llama 3.3 70B (Smartest)", "Llama 3.1 8B (Fastest)", "Mixtral 8x7B (Balanced)"],
        index=1, # Default to 8B now to avoid errors
        help="Switch brains if you hit rate limits or need more speed."
    )
    
    # Map selection to internal model names
    model_map = {
        "Llama 3.3 70B (Smartest)": "llama-3.3-70b-versatile",
        "Llama 3.1 8B (Fastest)": "llama-3.1-8b-instant",
        "Mixtral 8x7B (Balanced)": "mixtral-8x7b-32768"
    }
    
    st.session_state.llm_model = model_map[selected_model]
    st.session_state.llm_provider = "groq" # Keep groq as default for now
    
    with st.expander("🔑 Neural Key Vault", expanded=False):
        st.caption("Guests use system defaults. Enter your own key to use your personal quota.")
        
        # UI Status Badges
        using_groq = "🔵 Personal" if st.session_state.get("user_groq_key") else "🟢 System"
        using_gemini = "🔵 Personal" if st.session_state.get("user_gemini_key") else "🟢 System"
        
        st.markdown(f"**Groq Status:** `{using_groq}`")
        user_groq = st.text_input("Personal Groq Key", type="password", value=st.session_state.get("user_groq_key", ""), help="Override system key with your own.")
        
        st.markdown(f"**Gemini Status:** `{using_gemini}`")
        user_gemini = st.text_input("Personal Gemini Key", type="password", value=st.session_state.get("user_gemini_key", ""), help="Override system key with your own.")
        
        # Hidden inputs for other providers
        user_openai = st.text_input("OpenAI Key (Optional)", type="password", value=st.session_state.get("user_openai_key", ""))
        user_hf = st.text_input("HF Token (Optional)", type="password", value=st.session_state.get("user_hf_key", ""))

        st.session_state.user_groq_key = user_groq
        st.session_state.user_gemini_key = user_gemini
        st.session_state.user_openai_key = user_openai
        st.session_state.user_hf_key = user_hf

        if st.button("💾 Save My Keys Permanently", use_container_width=True):
            save_user_keys({
                "groq": user_groq, "gemini": user_gemini,
                "openai": user_openai, "hf": user_hf
            })
            st.toast("Personal keys secured! 🔐")
            
    st.divider()
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
