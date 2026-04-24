from utils.ui_components import load_css
import streamlit as st
from utils.api import call_api
import json

st.title("🔍 Insights & Future Work")
load_css("assets/styles.css")

if "insights" not in st.session_state or not st.session_state.insights:
    st.info("Run analysis in Smart Summary first.")
else:
    ins = st.session_state.insights
    st.markdown("#### 🧩 Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔑 Keywords**")
        keywords = ins.get("keywords", [])
        if keywords:
            for kw in keywords:
                st.info(kw)
        else:
            st.caption("No keywords found.")
            
    with col2:
        st.markdown("**💾 Datasets**")
        datasets = ins.get("datasets", [])
        if datasets:
            for ds in datasets:
                st.success(ds)
        else:
            st.caption("No datasets extracted.")
            
    with col3:
        st.markdown("**⚙️ Algorithms**")
        algorithms = ins.get("algorithms", [])
        if algorithms:
            for al in algorithms:
                st.warning(al)
        else:
            st.caption("No algorithms extracted.")

eli15 = st.toggle("🧒 Explain Like I'm 15")
if eli15 and "summary" in st.session_state:
    with st.spinner("Simplifying..."):
        simp = call_api("/simplify", {"text": json.dumps(st.session_state.summary)})
    st.success(simp.get("simplified", ""))

st.markdown("---")
if st.button("🔮 Generate Future Research Suggestions", type="primary"):
    if "paper_text" not in st.session_state:
        st.error("No paper detected! Please upload and analyze a PDF on the Home page first.")
    else:
        with st.spinner("Brainstorming future directions..."):
            fw = call_api("/future-work", {"text": st.session_state.paper_text})
        
        if fw.get("suggestions"):
            st.markdown("### 🚀 Future Work Ideas")
            for i, s in enumerate(fw["suggestions"], 1):
                if isinstance(s, str) and s.strip():
                    st.markdown(f"**{i}.** {s.strip()}")
                elif isinstance(s, dict) and "suggestion" in s: 
                     st.markdown(f"**{i}.** {s['suggestion']}")
