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
        padding: 60px 80px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        border: 1px solid #ccc;
        border-radius: 2px;
        height: 1120px; /* Fixed A4-like height */
        color: #000000 !important;
        transition: all 0.3s ease;
        overflow: hidden;
        position: relative;
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
        font_style = st.selectbox(
            "Font Family", 
            ["Times New Roman", "Arial", "Calibri", "Georgia", "Cambria", "Monospace"], 
            index=0
        )
        font_size = st.slider("Font Size (pt)", 8, 14, 11)
        line_spacing = st.select_slider("Line Spacing", options=[1.0, 1.15, 1.5, 2.0], value=1.15)
        show_page_nums = st.toggle("Show Page Info", value=True)
        
    st.divider()
    st.info("Select a template and customize your typography in the sidebar to live-update the preview.")

# --- Main UI ---
tab_input, tab_preview, tab_history = st.tabs(["🏗️ Structure Draft", "👁️ Digital Paper Preview", "📜 Draft Library"])

with tab_input:
    st.markdown('<div class="vision-panel">', unsafe_allow_html=True)
    st.markdown("### 📥 Source Materials")
    
    # --- Master Structuring Handbook Popover ---
    with st.popover("📘 Master Structuring Handbook", help="Deep structural guide for world-class research formatting"):
        st.markdown("## 🏛️ The Academic Blueprint")
        st.info("The AI acts as a **Mechanical Architect**. Provide your raw data in the sections below for the highest structural fidelity.")
        
        with st.expander("📝 1. Title & Abstract (The Hook)", expanded=True):
            st.markdown("""
            **Title**: Should be clear, concise, and contain your primary keyword.
            **Abstract**: A single paragraph (150-250 words). 
            - *Structure*: Motivation -> Problem -> Approach -> Results -> Conclusion.
            """)
            
        with st.expander("🔍 2. Introduction & Literature (The Context)"):
            st.markdown("""
            **Introduction**: Define the 'Why'. What gap are you filling in current research?
            **Literature Review**: Briefly mention previous work. 
            - *AI Tip*: You can just list authors and their findings; the AI will structure the narrative flow.
            """)
            
        with st.expander("🔬 3. Methodology (The Core)"):
            st.markdown("""
            **Methodology**: Describe your 'How'. 
            - Include: Dataset descriptions, algorithms, mathematical models, or experimental setups.
            - *Format*: Steps or raw data blocks work best here.
            """)
            
        with st.expander("📊 4. Results & Discussion (The Proof)"):
            st.markdown("""
            **Results**: Present the data. (e.g., 'Accuracy increased by 12%').
            **Discussion**: Interpret the data. What do these results mean for the field?
            """)
            
        with st.expander("🏁 5. Conclusion & References (The Legacy)"):
            st.markdown("""
            **Conclusion**: Summarize findings and suggest future paths.
            **References**: List your sources. 
            - *IEEE*: Use [1], [2] format.
            - *APA*: Use (Author, Year).
            - *AI Tip*: Just paste the URLs or raw citations; the AI will align them to your selected template.
            """)
            
        st.success("✨ **Pro Tip**: Use clear headers like 'Methodology:' or 'My Findings:' in your raw text to help the AI map your content with 100% precision.")

    paper_title = st.text_input(
        "Final Paper Title", 
        placeholder="e.g., Deep Learning in Quantum Computing: A Review"
    )
    raw_content = st.text_area(
        "Raw Research Content", 
        placeholder="Paste your messy notes, findings, or raw text blocks here...", 
        height=400
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🚀 Structuring & Formatting", use_container_width=True):
        if not paper_title or not raw_content:
            st.warning("Action Required: Please provide both a title and some research content.")
        else:
            with st.status("🧠 AI Architect is working...", expanded=True) as status:
                st.write("Extracting logical sections...")
                payload = {
                    "title": paper_title, 
                    "text": raw_content,
                    "template_name": template_name
                }
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
            pdf_bytes = export_as_pdf(paper, template_name, font_style, line_spacing)
            st.download_button(
                label="📥 Export as PDF",
                data=pdf_bytes,
                file_name=f"{paper.get('title', 'paper').replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_d:
            docx_bytes = export_as_docx(paper, template_name, font_style, line_spacing)
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
        
        # --- CONTINUOUS PREMIUM PREVIEW ---
        import html
        
        font_family_map = {
            "Times New Roman": "'Times New Roman', Times, serif",
            "Arial": "Arial, Helvetica, sans-serif",
            "Calibri": "Calibri, 'Segoe UI', Candara, Segoe, Optima, Arial, sans-serif",
            "Georgia": "Georgia, serif",
            "Cambria": "Cambria, 'Hoefler Text', 'Liberation Serif', Times, 'Times New Roman', serif",
            "Monospace": "'Courier New', Courier, monospace"
        }
        selected_font = font_family_map.get(font_style, "'Times New Roman', serif")
        
        # Escape all content strings
        title_esc = html.escape(str(paper.get('title', 'UNTITLED RESEARCH')))
        abstract_esc = html.escape(str(paper.get('abstract', '')))
        keywords_esc = html.escape(str(paper.get('keywords', '')))
        
        # 1. Header (Always Full Width)
        header_html = f"""
            <div class="a4-title-section">
                <h1>{title_esc}</h1>
                <div class="abstract-box"><strong>ABSTRACT:</strong> {abstract_esc}</div>
                <div class="abstract-box"><strong>KEYWORDS:</strong> {keywords_esc}</div>
                <hr>
            </div>
        """
        
        # 2. Body Content
        items = [
            ("I. Introduction", "introduction"),
            ("II. Literature Review", "lit_review"),
            ("III. Methodology", "methodology"),
            ("IV. Results & Discussion", "results"),
            ("V. Conclusion", "conclusion"),
            ("VI. Future Scope", "future_scope"),
            ("References", "references"),
        ]
        
        is_ieee = template_name == "IEEE"
        col_class = "ieee-columns" if is_ieee else "single-column"
        
        sections_html = ""
        for label, key in items:
            raw_content = paper.get(key, "")
            if not raw_content: continue
            
            content_esc = html.escape(str(raw_content))
            # References often span full width in IEEE
            div_class = "full-width" if key == "references" and is_ieee else ""
            
            sections_html += f"""
                <div class="{div_class}">
                    <div class="paper-section-head">{label}</div>
                    <div class="paper-body">{content_esc}</div>
                </div>
            """

        styles = f"""
        <style>
            .paper-stack {{
                background: #e2e8f0;
                padding: 50px 0;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .continuous-page {{
                background: white;
                color: black;
                width: 210mm;
                height: 297mm; /* Fixed A4 height */
                padding: 20mm 25mm;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                font-family: {selected_font};
                font-size: {font_size}pt;
                line-height: {line_spacing};
                box-sizing: border-box;
            }}
            .continuous-page h1 {{ text-align: center; margin-bottom: 25px; font-weight: bold; border:none; font-size: 1.8em; color: black !important; }}
            .abstract-box {{ text-align: justify; margin-bottom: 15px; font-style: italic; color: #333; }}
            .paper-section-head {{ font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #333; margin-top: 25px; margin-bottom: 10px; color: black !important; }}
            .paper-body {{ text-align: justify; margin-bottom: 15px; white-space: pre-wrap; color: #111 !important; }}
            .ieee-columns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
            .single-column {{ display: block; }}
            .full-width {{ grid-column: 1 / span 2; }}
            hr {{ border: 0; border-top: 1px solid #eee; margin: 20px 0; }}
        </style>
        """
        
        full_html = f"""
        <div class="paper-stack">
            <div class="continuous-page">
                {header_html}
                <div class="{col_class}">
                    {sections_html}
                </div>
            </div>
        </div>
        """
        
        st.html(styles + full_html)

with tab_history:
    st.markdown("### 🏛️ Your Academic Library")
    st.caption("Manage and reload your previously structured research drafts.")
    history = load_history()
    if not history:
        st.info("Your library is empty. Format your first paper to see it here!")
    else:
        for i, p in enumerate(history):
            with st.container(border=True):
                col_info, col_act = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**📄 {p.get('title', 'Untitled Paper')[:80]}...**")
                    st.caption(f"📅 Structured on: {p.get('timestamp', 'Unknown Date')}")
                with col_act:
                    if st.button("🔄 Load", key=f"load_{i}", use_container_width=True):
                        st.session_state.formatted_paper = p
                        st.success("Draft loaded! Swipe to Preview tab.")
                        st.rerun()
                    if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                        delete_from_history(i)
                        st.rerun()
