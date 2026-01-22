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
    use_general_knowledge = st.toggle("🌍 Enable General AI Knowledge", value=False, help="Allow the model to use outside knowledge combined with the paper.")

    user_input = st.chat_input("Ask anything about this paper...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            combined_context = "\n\n".join(active_contexts)
            resp = call_api("/chat", {
                "query": user_input, 
                "context": combined_context,
                "use_general_knowledge": use_general_knowledge
            })
        answer = resp.get("answer", "Sorry, no response.")
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
