# pages/_Visual_QA.py
"""
Module 5.1 – Visual Q&A (Page Inspector)
Extract and analyse specific PDF pages using Groq + pdfplumber.
"""

import streamlit as st
import io
from utils.api import call_api
from utils.vision_utils import extract_page_content, render_page_preview, get_page_count

st.title("🔬 Visual Q&A – Page Inspector")
st.markdown(
    "Upload a research PDF, select a page, and ask questions about its content — "
    "including tables, figures, and data."
)

uploaded = st.file_uploader("📄 Upload Research PDF", type=["pdf"], key="visual_qa_upload")

if uploaded:
    pdf_bytes = uploaded.read()
    total_pages = get_page_count(pdf_bytes)

    if total_pages == 0:
        st.error("Could not read this PDF. Please try another file.")
        st.stop()

    st.success(f"✅ Loaded **{uploaded.name}** — {total_pages} pages")

    col1, col2 = st.columns([1, 2])
    with col1:
        page_num = st.number_input(
            "Select Page", min_value=1, max_value=total_pages,
            value=1, step=1, key="visual_qa_page"
        )

    with col2:
        st.markdown(f"**Page {page_num} of {total_pages}**")

    # --- Preview ---
    with st.spinner("Rendering page preview..."):
        preview_img = render_page_preview(pdf_bytes, page_num)

    preview_col, content_col = st.columns([1, 1])

    with preview_col:
        st.markdown("#### 🖼️ Page Preview")
        if preview_img:
            st.image(preview_img, use_container_width=True)
        else:
            st.info("Preview unavailable for this page.")

    with content_col:
        st.markdown("#### 📋 Extracted Content")
        with st.spinner("Extracting page content..."):
            page_data = extract_page_content(pdf_bytes, page_num)

        if "error" in page_data:
            st.error(page_data["error"])
            st.stop()

        with st.expander("Raw Text", expanded=False):
            st.text(page_data.get("text", "No text found on this page."))

        if page_data.get("tables"):
            with st.expander(f"📊 Tables ({len(page_data['tables'])} found)", expanded=True):
                for t_md in page_data["tables"]:
                    st.markdown(t_md)
        else:
            st.info("No tables detected on this page.")

    st.markdown("---")

    # --- Q&A Section ---
    st.markdown("#### ❓ Ask About This Page")
    question = st.text_input(
        "Your question",
        placeholder="e.g. What does Table 2 show? What are the key results on this page?",
        key="visual_qa_question"
    )

    if st.button("🔍 Get Answer", key="visual_qa_submit") and question.strip():
        combined_content = page_data.get("combined_markdown", "")
        if not combined_content.strip():
            st.warning("No content was extracted from this page to analyse.")
        else:
            with st.spinner("Analysing page and generating answer..."):
                result = call_api("/visual-qa", {
                    "page_content": combined_content,
                    "question": question
                })
            if "answer" in result:
                st.markdown("#### 💡 Answer")
                st.markdown(result["answer"])
            else:
                st.error(result.get("error", "Failed to get an answer."))
    elif not uploaded:
        st.info("Upload a PDF to begin.")
