# pages/_Citation_Graph.py
"""
Module 5.4 – Citation Influence Graph
Fetches paper metadata from OpenAlex (free, no key needed) and renders
an interactive citation network using Pyvis embedded in Streamlit.
"""

from utils.ui_components import load_css
import streamlit as st
import json
import os
import tempfile
from utils.citation_utils import search_paper_openalex, get_citation_network, format_authors

st.title("🕸️ Citation Influence Graph")
load_css("assets/styles.css")
st.markdown(
    "Explore how a research paper influences and is influenced by others. "
    "Powered by the **OpenAlex API** — completely free, no key required."
)

st.markdown("---")

# ── Paper Search ───────────────────────────────────────────────────────────────
st.markdown("### 🔎 Find a Paper")
title_input = st.text_input(
    "Enter paper title",
    placeholder="e.g. Attention is All You Need",
    key="citation_title"
)

max_refs = st.slider(
    "Max references to show", min_value=5, max_value=30, value=15,
    help="Higher values fetch more citation connections but may be slower."
)

if st.button("🔍 Fetch Citation Network", key="citation_fetch") and title_input.strip():

    # Step 1: search for the paper
    with st.spinner("Searching OpenAlex for the paper..."):
        work = search_paper_openalex(title_input)

    if not work or "error" in work:
        st.error(
            f"Could not find a paper matching **\"{title_input}\"**. "
            "Try a more specific title or check your spelling."
        )
        if work and "error" in work:
            st.caption(f"API error: {work['error']}")
        st.stop()

    # Show found paper info
    work_id = work.get("id", "").split("/")[-1]
    found_title = work.get("title", "Unknown")
    found_year = work.get("publication_year", "N/A")
    found_citations = work.get("cited_by_count", 0)
    found_authors = format_authors(work)

    st.success(f"✅ Found: **{found_title}**")
    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.metric("Year", found_year)
    info_col2.metric("Total Citations", f"{found_citations:,}")
    info_col3.metric("Authors", found_authors[:30] + "…" if len(found_authors) > 30 else found_authors)

    # Step 2: build citation network
    with st.spinner("Building citation network (fetching references)..."):
        network = get_citation_network(work_id, max_references=max_refs)

    if "error" in network:
        st.error(f"Could not build citation network: {network['error']}")
        st.stop()

    nodes = network["nodes"]
    edges = network["edges"]
    root_id = network["root_id"]

    st.info(f"📊 Graph: **{len(nodes)} papers**, **{len(edges)} citation links**")

    # ── Build Pyvis graph ─────────────────────────────────────────────────────
    try:
        from pyvis.network import Network

        net = Network(height="600px", width="100%", bgcolor="#0e1117", font_color="white")
        net.set_options(json.dumps({
            "nodes": {
                "shape": "dot",
                "scaling": {"min": 10, "max": 40},
                "font": {"size": 12, "face": "Inter, Arial"},
            },
            "edges": {
                "color": {"color": "#4a9eff", "opacity": 0.7},
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
                "smooth": {"type": "curvedCW", "roundness": 0.2},
            },
            "physics": {
                "stabilization": {"iterations": 150},
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "centralGravity": 0.3,
                    "springLength": 150,
                },
            },
            "interaction": {"hover": True, "tooltipDelay": 100},
        }))

        for node in nodes:
            nid = node["id"]
            is_root = node.get("is_root", False)
            label = node["title"][:40] + "…" if len(node["title"]) > 40 else node["title"]
            year = node.get("year", "N/A")
            cites = node.get("citations", 0)
            author = node.get("author", "")
            doi = node.get("doi", "")
            tooltip = (
                f"<b>{node['title']}</b><br>"
                f"Author: {author}<br>"
                f"Year: {year} | Citations: {cites:,}"
            )
            if doi:
                tooltip += f"<br>DOI: {doi}"

            # Size nodes by citation count (scaled)
            import math
            size = 20 + min(30, int(math.log1p(cites) * 3))
            color = "#ff6b35" if is_root else "#4a9eff"
            border = "#ffffff" if is_root else "#2a5fcc"

            net.add_node(
                nid,
                label=label,
                title=tooltip,
                size=size,
                color={"background": color, "border": border, "highlight": {"background": "#ffd700"}},
                borderWidth=3 if is_root else 1,
            )

        for edge in edges:
            net.add_edge(edge["source"], edge["target"], title=edge.get("label", "cites"))

        # Save and embed HTML
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w") as tmp:
            html_str = net.generate_html()
            tmp.write(html_str)
            tmp_path = tmp.name

        with open(tmp_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        os.unlink(tmp_path)

        st.markdown("#### 🕸️ Interactive Citation Graph")
        st.markdown(
            "_Drag nodes to rearrange. Hover for paper details. "
            "🔴 = selected paper, 🔵 = referenced papers._"
        )
        st.components.v1.html(html_content, height=650, scrolling=False)

    except ImportError:
        st.error("Pyvis is not installed. Run: `pip install pyvis`")
        st.stop()

    # ── Paper List ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Papers in Network")
    for node in sorted(nodes, key=lambda x: x.get("citations", 0), reverse=True):
        badge = "🔴 **[ROOT]**" if node.get("is_root") else "🔵"
        doi_link = f" — [DOI]({node['doi']})" if node.get("doi") else ""
        st.markdown(
            f"{badge} **{node['title']}** ({node.get('year', 'N/A')}) "
            f"— {node.get('author', '')} "
            f"— {node.get('citations', 0):,} citations{doi_link}"
        )

else:
    st.markdown("Enter a paper title above and click **Fetch Citation Network** to begin.")
    st.markdown("#### 💡 Example papers to try:")
    for example in [
        "Attention is All You Need",
        "BERT: Pre-training of Deep Bidirectional Transformers",
        "Deep Residual Learning for Image Recognition",
        "Generative Adversarial Networks",
    ]:
        st.markdown(f"- {example}")
