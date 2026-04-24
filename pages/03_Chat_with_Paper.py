# pages/_Chat_with_Paper.py
from utils.ui_components import load_css
import streamlit as st
from utils.api import call_api
import time

# Styling for the RAG Badge
st.markdown("""
    <style>
    .rag-badge {
        background-color: #4CAF50;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
        float: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Chat with Paper")
load_css("assets/styles.css")

if "messages" not in st.session_state:
    st.session_state.messages = []

active_contexts = []
paper_name = st.session_state.get("paper_name")
paper_text = st.session_state.get("paper_text")

if paper_text:
    active_contexts.append(f"--- Main Paper ({paper_name or 'Uploaded Paper'}) ---\n{paper_text}")
    
    # --- AUTO-INDEXING SYSTEM (True RAG Upgrade) ---
    if paper_name:
        from utils.rag_utils import is_paper_indexed
        if not is_paper_indexed(paper_name):
            with st.status(f"⚡ Semantic Indexing: {paper_name}...", expanded=False) as status:
                st.write("Chunking document into semantic blocks...")
                time.sleep(0.5)
                st.write("Generating local embeddings (all-MiniLM-L6-v2)...")
                call_api("/rag-add", {"paper_name": paper_name, "text": paper_text})
                status.update(label=f"✅ {paper_name} Indexed for True RAG", state="complete")
        else:
            st.markdown(f'<div class="rag-badge">⚡ RAG ENABLED</div>', unsafe_allow_html=True)

if st.session_state.get("paper_a_text"):
    active_contexts.append(f"--- Paper A (Comparison) ---\n{st.session_state.paper_a_text}")

if st.session_state.get("paper_b_text"):
    active_contexts.append(f"--- Paper B (Comparison) ---\n{st.session_state.paper_b_text}")

if not active_contexts:
    st.warning("Upload a paper in Smart Summary OR Compare Papers first.")
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Options
    opt_col1, opt_col2 = st.columns(2)
    use_general_knowledge = opt_col1.toggle(
        "🌍 Enable General AI Knowledge", value=False,
        help="Allow the model to use outside knowledge combined with the paper."
    )
    use_rag_history = opt_col2.toggle(
        "🗂️ Search Historical Library", value=True,
        help="Automatically query your Local Insights Library for relevant context from past papers."
    )

    user_input = st.chat_input("Ask anything about this paper...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # RAG Retrieval System
        historical_chunks = None
        active_paper_chunks = None
        rag_sources = []
        
        with st.spinner("Retrieving relevant context..."):
            # 1. Active Paper RAG (Precise lookup in CURRENT document)
            if paper_name:
                try:
                    from utils.rag_utils import query_library
                    # Specific query for the current paper's chunks ONLY
                    active_paper_chunks = query_library(user_input, n_results=6, paper_name=paper_name) 
                except Exception:
                    pass

            # 2. Historical Library RAG (Cross-paper search)
            if use_rag_history:
                try:
                    from utils.rag_utils import query_library, get_library_stats
                    # Note: Existing query_library searches ALL papers. 
                    # For historical search, we can treat it as a broad search.
                    historical_chunks = query_library(user_input, n_results=4)
                    rag_sources = list({c["paper_name"] for c in historical_chunks if c["paper_name"] != paper_name}) 
                except Exception:
                    pass

        with st.spinner("Thinking..."):
            combined_context = "\n\n".join(active_contexts)
            resp = call_api("/chat", {
                "query": user_input,
                "context": combined_context,
                "use_general_knowledge": use_general_knowledge,
                "historical_context": historical_chunks,
                "active_paper_chunks": active_paper_chunks
            })

        answer = resp.get("answer", "Sorry, no response.")
        st.session_state.messages.append({"role": "assistant", "content": answer})

        with st.chat_message("assistant"):
            st.markdown(answer)
            # Show which past papers contributed historical context
            if rag_sources:
                with st.expander(f"📚 Historical context from {len(rag_sources)} past paper(s)", expanded=False):
                    for src in rag_sources:
                        st.markdown(f"- 📄 `{src}`")
