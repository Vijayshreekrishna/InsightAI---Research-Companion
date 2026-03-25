# pages/_Chat_with_Paper.py
import streamlit as st
from utils.api import call_api

st.title("💬 Chat with Paper")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Consolidate context from different pages
active_contexts = []
if st.session_state.get("paper_text"):
    active_contexts.append(f"--- Main Paper ({st.session_state.get('paper_name', 'Uploaded Paper')}) ---\n{st.session_state.paper_text}")

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

        # RAG: retrieve historical context if enabled
        historical_chunks = None
        rag_sources = []
        if use_rag_history:
            try:
                from utils.rag_utils import query_library, get_library_stats
                stats = get_library_stats()
                if stats.get("total_chunks", 0) > 0:
                    historical_chunks = query_library(user_input, n_results=4)
                    rag_sources = list({c["paper_name"] for c in historical_chunks}) if historical_chunks else []
            except Exception:
                pass  # RAG library not yet initialised — skip silently

        with st.spinner("Thinking..."):
            combined_context = "\n\n".join(active_contexts)
            resp = call_api("/chat", {
                "query": user_input,
                "context": combined_context,
                "use_general_knowledge": use_general_knowledge,
                "historical_context": historical_chunks,
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
