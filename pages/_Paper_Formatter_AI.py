import streamlit as st
import time
from utils.ui_components import load_css, title_banner
from utils.api import call_api
from utils.paper_utils import (
    get_template_config, export_as_pdf, export_as_docx, 
    save_to_history, load_history, delete_from_history
)

# Page configuration
st.set_page_config(page_title="Paper Formatter AI", page_icon="📝", layout="wide")
load_css("assets/styles.css")
title_banner()

# Custom CSS for the "Premium Paper" look
st.markdown("""
<style>
    .paper-sheet {
        background: #ffffff !important;
        margin: 20px auto;
        padding: 50px 70px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        border: 1px solid #ccc;
        border-radius: 2px;
        min-height: 1000px;
        color: #000000 !important;
        transition: all 0.3s ease;
        overflow: hidden;
    }
    .paper-sheet h1 { 
        text-align: center; 
        color: #000 !important; 
        margin-bottom: 30px; 
        border: none; 
        font-weight: bold;
    }
    .paper-section-head { 
        font-weight: 800; 
        text-transform: uppercase; 
        border-bottom: 2px solid #333; 
        margin-top: 25px; 
        margin-bottom: 12px;
        color: #111 !important;
        letter-spacing: 1.5px;
        font-size: 1.1em;
    }
    .paper-body { 
        text-align: justify; 
        margin-bottom: 20px; 
        color: #222 !important;
        white-space: pre-wrap; /* Preserve AI line breaks */
    }
    
    /* IEEE 2-Column Simulation */
    .ieee-columns {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 40px;
    }
    
    .full-width { grid-column: 1 / span 2; }
</style>
""", unsafe_allow_html=True)

st.title("📄 Premium Paper Formatter")
st.caption("AI-Powered Academic Draft Structuring")

# --- Sidebar / Controls ---
with st.sidebar:
    st.header("🎨 Design System")
    
    template_name = st.selectbox(
        "Academic Template",
        ["Generic University", "IEEE", "ACM", "Springer"]
    )
    
    with st.expander("📝 Typography & Layout", expanded=True):
        font_style = st.selectbox("Font Family", ["Serif", "Sans-Serif", "Monospace"], index=0)
        font_size = st.slider("Font Size (pt)", 8, 14, 11)
        line_spacing = st.select_slider("Line Spacing", options=[1.0, 1.15, 1.5, 2.0], value=1.15)
        show_page_nums = st.toggle("Show Page Info", value=True)
        
    st.divider()
    st.markdown("### 📜 Draft History")
    history = load_history()
    if not history:
        st.info("No saved papers yet.")
    else:
        for p in history:
            col_list, col_del = st.columns([4, 1])
            if col_list.button(f"📄 {p['title'][:20]}...", key=f"hist_{p['id']}"):
                st.session_state.formatted_paper = p
            if col_del.button("🗑️", key=f"del_{p['id']}"):
                delete_from_history(p['id'])
                st.rerun()

# --- Main UI ---
tab_input, tab_preview = st.tabs(["🏗️ Structure Draft", "👁️ Digital Paper Preview"])

with tab_input:
    st.markdown("### 📥 Source Materials")
    paper_title = st.text_input("Final Paper Title", placeholder="e.g., Deep Learning in Quantum Computing: A Review")
    raw_content = st.text_area("Raw Research Content", placeholder="Paste your messy notes, findings, or raw text blocks here...", height=400)
    
    if st.button("🚀 Structuring & Formatting", use_container_width=True):
        if not paper_title or not raw_content:
            st.warning("Action Required: Please provide both a title and some research content.")
        else:
            with st.status("🧠 AI Architect is working...", expanded=True) as status:
                st.write("Extracting logical sections...")
                payload = {"title": paper_title, "text": raw_content}
                result = call_api("/format-paper", payload)
                if result and "error" not in result:
                    st.session_state.formatted_paper = result
                    status.update(label="✅ Formatting Complete!", state="complete", expanded=False)
                    st.toast("Draft Ready! Swipe to Preview tab.")
                else:
                    st.error("Error: AI generation encountered a problem. Check API keys.")

with tab_preview:
    if "formatted_paper" not in st.session_state:
        st.info("Nothing to show yet. Please structure a draft in the first tab.")
    else:
        paper = st.session_state.formatted_paper
        
        # Action Bar
        col_s, col_p, col_d = st.columns([1, 1, 1])
        with col_s:
            if st.button("📂 Save Draft to Library", use_container_width=True):
                save_to_history(paper)
                st.success("Draft saved!")
                
        with col_p:
            pdf_bytes = export_as_pdf(paper, template_name, font_style)
            st.download_button(
                label="📥 Export as PDF",
                data=pdf_bytes,
                file_name=f"{paper.get('title', 'paper').replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_d:
            docx_bytes = export_as_docx(paper, template_name, font_style)
            st.download_button(
                label="📥 Export as Word (DOCX)",
                data=docx_bytes,
                file_name=f"{paper.get('title', 'paper').replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        st.divider()

        # Check for non-structured response
        if "raw_response" in paper:
            st.warning("⚠️ The AI provided a non-structured response. Displaying raw content below.")
            st.markdown(f"""
                <div class="paper-sheet" style="font-family: serif; padding: 40px;">
                    <h2>Raw Drafting Output</h2>
                    <div class="paper-body">{paper['raw_response']}</div>
                </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # --- Premium Preview ---
        font_family_map = {
            "Serif": "'Times New Roman', Times, serif",
            "Sans-Serif": "'Inter', 'Roboto', Arial, sans-serif",
            "Monospace": "'Courier New', Courier, monospace"
        }
        selected_font = font_family_map.get(font_style, "serif")
        
        # Determine columns
        is_ieee = template_name == "IEEE"
        column_class = "ieee-columns" if is_ieee else ""
        
        header_html = f"""
            <div class="paper-sheet" style="font-family: {selected_font}; font-size: {font_size}pt; line-height: {line_spacing};">
                <h1>{paper.get('title', 'UNTITLED RESEARCH')}</h1>
                <div class="paper-body"><strong>ABSTRACT:</strong> {paper.get('abstract', '')}</div>
                <div class="paper-body"><strong>KEYWORDS:</strong> {paper.get('keywords', '')}</div>
                <hr>
                <div class="{column_class}">
        """
        
        footer_html = """
                </div>
            </div>
        """
        
        # Sections
        sections_html = ""
        items = [
            ("I. Introduction", "introduction"),
            ("II. Literature Review", "lit_review"),
            ("III. Methodology", "methodology"),
            ("IV. Results & Discussion", "results"),
            ("V. Conclusion", "conclusion"),
            ("VI. Future Scope", "future_scope"),
            ("References", "references"),
        ]
        
        for i, (label, key) in enumerate(items):
            content = paper.get(key, "")
            if not content: continue
            
            # References often span full width even in 2-column
            div_class = "full-width" if key == "references" and is_ieee else ""
            
            sections_html += f"""
                <div class="{div_class}">
                    <div class="paper-section-head">{label}</div>
                    <div class="paper-body">{content}</div>
                </div>
            """
            
        st.markdown(header_html + sections_html + footer_html, unsafe_allow_html=True)
