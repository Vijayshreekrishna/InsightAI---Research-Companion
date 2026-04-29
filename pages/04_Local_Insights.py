# pages/_Local_Insights.py
"""
Module 5.3 – Local Insights Library (Semantic RAG Module)
Persistent semantic search across all uploaded papers using 
ChromaDB + sentence-transformers. Works entirely offline after setup.
"""

from utils.ui_components import load_css
import streamlit as st
from utils.api import call_api
from utils.pdf_utils import extract_text_from_pdf
from utils.rag_utils import get_library_stats, delete_paper_from_library
import time

st.title("📚 Local Insights Library")
load_css("assets/styles.css")
st.markdown(
    "Build a **persistent semantic library** of research papers. "
    "Ask cross-paper questions and get grounded answers from your entire collection."
)

# ── Library Status ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Library Status")

stats = get_library_stats()
total = stats.get("total_chunks", 0)
papers = stats.get("papers", [])

if stats.get("error"):
    st.error(f"Library error: {stats.get('error')}")

if total == 0:
    st.info("📭 Your library is empty. Add papers below to get started.")
else:
    col1, col2 = st.columns(2)
    col1.metric("Total Papers", len(papers))
    col2.metric("Total Indexed Chunks", total)

    with st.expander(f"📋 Stored Papers ({len(papers)})", expanded=True):
        for p in papers:
            pcol1, pcol2 = st.columns([5, 1])
            pcol1.markdown(f"📄 {p}")
            if pcol2.button("🗑️", key=f"del_{p}", help=f"Remove {p}"):
                result = delete_paper_from_library(p)
                if result.get("status") == "success":
                    st.success(f"Removed **{p}** from library.")
                    st.rerun()
                else:
                    st.error(result.get("error", "Deletion failed."))

# ── Add Papers ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ➕ Add Papers to Library")
st.markdown(
    "Papers are chunked, embedded, and stored locally — they persist across sessions."
)

new_papers = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    key="lib_upload"
)

if new_papers and st.button("📥 Add to Library", key="lib_add"):
    progress = st.progress(0)
    for i, f in enumerate(new_papers):
        with st.spinner(f"Processing **{f.name}**..."):
            text = extract_text_from_pdf(f)
            result = call_api("/rag-add", {"paper_name": f.name, "text": text})
        if result.get("status") == "success":
            st.success(
                f"✅ **{f.name}** added — {result['chunks_added']} chunks indexed."
            )
        else:
            st.error(f"❌ Failed to add **{f.name}**: {result.get('error', 'Unknown error')}")
        progress.progress((i + 1) / len(new_papers))
    time.sleep(2)
    st.rerun()

# ── Cross-Paper Q&A ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🔍 Search Your Library")

if total == 0:
    st.warning("Add papers to your library first before querying.")
else:
    query = st.text_input(
        "Ask a question across all your stored papers",
        placeholder="e.g. What transformer architectures have been used for medical imaging?",
        key="lib_query"
    )

    n_results = st.slider("Number of chunks to retrieve", min_value=3, max_value=10, value=5)

    if st.button("🔎 Search Library", key="lib_search") and query.strip():
        from utils.rag_utils import query_library

        with st.spinner("Searching semantic library..."):
            chunks = query_library(query, n_results=n_results)

        if not chunks:
            st.warning("No relevant content found. Try rephrasing your question.")
        else:
            # Show sources
            with st.expander(f"📎 Retrieved Sources ({len(chunks)} chunks)", expanded=False):
                for i, chunk in enumerate(chunks):
                    st.markdown(
                        f"**[{i+1}]** From: `{chunk['paper_name']}` "
                        f"(chunk {chunk['chunk_index']}, distance: {chunk['distance']})"
                    )
                    st.text(chunk["text"][:300] + "...")
                    st.markdown("---")

            # Generate grounded answer
            with st.spinner("Generating answer from retrieved content..."):
                result = call_api("/rag-answer", {
                    "question": query,
                    "chunks": chunks
                })

            st.markdown("#### 💡 Answer")
            st.markdown(result.get("answer", "No answer generated."))
