# utils/api.py
import os
from dotenv import load_dotenv
from gtts import gTTS
import base64
import tempfile
import json
import re
from utils.llm_factory import get_llm_provider

# Load environment variables (from .env)
load_dotenv()

# -----------------------------
# Helper functions for LLM
# -----------------------------
def _truncate(text: str, limit: int) -> str:
    # pyre-ignore
    return text[:limit]

def summarize_paper(text: str):
    """Use configured LLM to summarize research paper text into sections."""
    provider = get_llm_provider()
    prompt = f"""
    You are an expert academic researcher. Provide a comprehensive, high-detail summary of this research paper.
    
    CRITICAL INSTRUCTIONS:
    1. **Be Comprehensive**: Do not be brief. Expand on every point to provide depth. 
    2. **Include Data**: You MUST include specific quantitative results, metrics, and exact figures from the paper.
    3. **Methodology Depth**: Describe the steps, architecture, and mathematical models in detail.
    4. **Strict Citations**: Cite the page number for every specific claim or figure using [Page X].
    5. **Source Only**: Use ONLY the provided text.

    Sections to Generate:
    - TL;DR Summary (A thorough paragraph, not just one sentence)
    - Abstract Summary (Detailed breakdown of the core problem and solution)
    - Methodology Overview (Deep dive into the technical approach, architecture, and algorithms)
    - Results & Findings (Comprehensive list of all key metrics, comparisons, and performance numbers)
    - Limitations (Detailed analysis of constraints and future work mentioned)

    Return your answer as structured JSON with keys:
    tldr, abstract, methodology, results, limitations.

    Research Paper Text:
    {_truncate(text, 15000)}
    """
    response_text = provider.generate_content(prompt)
    return _extract_json(response_text)


from typing import Optional

def chat_with_paper(query: str, context: str, use_general_knowledge: bool = False, historical_context: Optional[list] = None):
    """Ask configured LLM a question about the uploaded paper, optionally augmented with RAG history."""
    provider = get_llm_provider()

    # Build historical context block
    history_block = ""
    if historical_context:
        history_block = "\n\n[Historical Library Context – from past uploaded papers]\n"
        for hit in historical_context:
            history_block += f"\n[From: {hit['paper_name']}]\n{hit['text']}\n"

    if use_general_knowledge:
        prompt = f"""
You are a helpful research assistant. You have access to the following research paper content.

Answer the user's question. You may use the paper content AND your general knowledge.

IMPORTANT INSTRUCTIONS:
1. Prioritize information from the paper.
2. If you use information from the paper, cite it with [Page X].
3. If historical context from past papers is provided, mention which past paper it came from.
4. If the answer requires outside knowledge, you may provide it, but make it clear.

Paper Text:
{_truncate(context, 10000)}
{history_block}
Question:
{query}
"""
    else:
        prompt = f"""
You are a strict research assistant. Answer the question using the provided paper text.
If historical context from past papers is also provided, you may use it and cite the paper name.
If the answer is not in either source, state "I cannot find this information in the available papers."

IMPORTANT: Provide the page number for answers from the current paper using [Page X].
For historical context answers, cite the paper name in brackets, e.g. [From: paper_name.pdf].

Paper Text:
{_truncate(context, 10000)}
{history_block}
Question:
{query}
"""

    response_text = provider.generate_content(prompt)
    return {"answer": response_text}


def extract_insights(text: str):
    """Extract keywords, datasets, and algorithms from the paper."""
    provider = get_llm_provider()
    prompt = f"""
    From this research paper text, extract the following:
    - Top 5 keywords
    - Datasets used
    - Algorithms mentioned

    IMPORTANT: Cite the page number where each dataset/algorithm is found, e.g. "ResNet-50 [Page 3]".

    Return a valid JSON object with specific lowercase keys: "keywords", "datasets", "algorithms".
    Each key must map to a list of strings.
    Example: {{ "keywords": ["AI"], "datasets": ["MNIST"], "algorithms": ["CNN"] }}
    
    Text:
    {_truncate(text, 10000)}
    """
    response_text = provider.generate_content(prompt)
    return _extract_json(response_text)


def simplify_summary(text: str):
    """Simplify the summary for a younger audience."""
    provider = get_llm_provider()
    prompt = f"""
    Simplify this research summary as if explaining to a 15-year-old. Use short, clear sentences:
    {_truncate(text, 4000)}
    """
    response_text = provider.generate_content(prompt)
    return {"simplified": response_text}


def future_research_ideas(text: str):
    """Suggest possible future research directions."""
    provider = get_llm_provider()
    prompt = f"""
    Based on this paper, suggest 3-5 possible future research directions or open problems.
    
    Return a structured JSON with a single key "suggestions", which is a list of strings.
    Example: {{ "suggestions": ["Idea 1", "Idea 2", "Idea 3"] }}

    Research Paper Text:
    {_truncate(text, 8000)}
    """
    response_text = provider.generate_content(prompt)
    return _extract_json(response_text)


# -----------------------------
# API Dispatcher
# -----------------------------
def call_api(path: str, payload: dict):
    text = payload.get("text", "")
    query = payload.get("query", "")
    context = payload.get("context", "")
    use_general_knowledge = payload.get("use_general_knowledge", False)

    if path == "/summarize":
        return summarize_paper(text)
    elif path == "/chat":
        return chat_with_paper(
            query, context, use_general_knowledge,
            historical_context=payload.get("historical_context", None)
        )
    elif path == "/extract":
        return extract_insights(text)
    elif path == "/simplify":
        return simplify_summary(text)
    elif path == "/future-work":
        return future_research_ideas(text)
    elif path == "/tts":
        return generate_tts(payload.get("text", ""))
    elif path == "/compare":
        return compare_papers(payload.get("text_a", ""), payload.get("text_b", ""))
    elif path == "/visual-qa":
        return visual_qa(payload.get("page_content", ""), payload.get("question", ""))
    elif path == "/podcast-script":
        return generate_podcast_script(payload.get("text", ""))
    elif path == "/rag-answer":
        return rag_answer(payload.get("question", ""), payload.get("chunks", []))
    elif path == "/rag-add":
        return rag_add_paper(payload.get("paper_name", ""), payload.get("text", ""))
    else:
        return {"error": f"Unknown path: {path}"}


# -----------------------------
# Helper: Extract JSON safely
# -----------------------------
def _extract_json(response_text: str):
    """Extract and safely parse JSON from model output."""
    try:
        # cleanup code blocks if present
        cleaned_text = re.sub(r'```json\s*', '', response_text)
        cleaned_text = re.sub(r'```', '', cleaned_text)
        
        json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(cleaned_text) # Attempt direct load
    except Exception:
        # fallback heuristic if model doesn't return proper JSON
        return {"raw_response": response_text}


def generate_tts(text: str):
    """Generate an MP3 from text and return it as base64 for Streamlit playback."""
    text = text.strip()
    if not text:
        return {"error": "Empty text — nothing to read."}

    try:
        # Shorten overly long text to avoid gTTS limit
        if len(text) > 4500:
            text = _truncate(text, 4500) + " ... summary truncated."

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts = gTTS(text=text, lang="en", slow=False, tld="com")
            tts.save(tmp.name)
            with open(tmp.name, "rb") as f:
                audio_bytes = f.read()

        # Encode to base64 for Streamlit playback
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        os.remove(tmp.name)
        return {"audio_base64": audio_base64}

    except Exception as e:
        return {"error": f"TTS generation failed: {str(e)}"}
    
def compare_papers(text_a: str, text_b: str):
        """Use configured LLM to compare two research papers and return structured insights."""
        provider = get_llm_provider()
        prompt = f"""
        You are an academic comparison assistant.

        Compare these two research papers and provide:
        1. 3–5 key differences between them
        2. 3–5 key similarities
        3. A short summary paragraph highlighting which paper offers stronger contributions or novelty

        Format your response as JSON with keys:
        - "differences": [list of strings]
        - "similarities": [list of strings]
        - "summary": "string"

        --- PAPER A ---
        {_truncate(text_a, 15000)}

        --- PAPER B ---
        {_truncate(text_b, 15000)}
        """

        response_text = provider.generate_content(prompt)
        return _extract_json(response_text)


# -----------------------------------------------
# New Module Functions
# -----------------------------------------------

def visual_qa(page_content: str, question: str) -> dict:
    """Answer a question about a specific PDF page using its extracted text and tables."""
    provider = get_llm_provider()
    prompt = f"""
You are an expert at interpreting research paper content including tables, figures, and data.

A user is viewing a specific page from a research PDF. Below is the structured content extracted 
from that page (text + any tables). Answer their question ONLY based on this page content.

If the page contains a table, interpret it carefully and explain the values.
If a figure is mentioned in the text, describe what it likely represents.
If the answer is not present on this page, say so clearly.

Page Content:
{_truncate(page_content, 6000)}

User Question: {question}
"""
    response_text = provider.generate_content(prompt)
    return {"answer": response_text}


def generate_podcast_script(text: str) -> dict:
    """Generate a two-person academic podcast dialogue from paper text."""
    provider = get_llm_provider()
    prompt = f"""
You are a podcast script writer for an academic research show called "InsightCast".

Create a natural, engaging two-person dialogue about the research paper below.

Personas:
- Dr. Aisha (Expert): A seasoned researcher who explains concepts deeply and cites specifics.
- Jamie (Host): An enthusiastic, curious interviewer who asks questions a smart non-expert would ask.

Guidelines:
1. Start with Jamie welcoming the audience and introducing the paper topic.
2. Cover: the problem being solved, the key methodology, the main results, and why it matters.
3. Include at least ONE moment where Jamie expresses surprise or excitement at a result.
4. End with Dr. Aisha giving a forward-looking statement about the research.
5. Keep it conversational, engaging, and 8–12 dialogue turns total.
6. Do NOT use asterisks or markdown — plain text only.

Format each line as:
Jamie: [line]
Dr. Aisha: [line]

Research Paper:
{_truncate(text, 8000)}
"""
    response_text = provider.generate_content(prompt)
    return {"script": response_text}


def rag_answer(question: str, chunks: list) -> dict:
    """Answer a question grounded entirely in RAG-retrieved chunks."""
    provider = get_llm_provider()
    if not chunks:
        return {"answer": "No relevant documents found in the library. Please add papers first."}

    context_block = ""
    for i, chunk in enumerate(chunks):
        context_block += f"\n[{i+1}. From: {chunk.get('paper_name', 'Unknown')}]\n{chunk.get('text', '')}\n"

    prompt = f"""
You are a research assistant with access to a library of academic papers.

Answer the user's question using ONLY the retrieved excerpts below.
For each claim, cite the paper name in brackets, e.g. [From: paper_name.pdf].
If the information is not in the excerpts, say "This topic was not found in the current library."

Retrieved Excerpts:
{context_block[:8000]}

Question: {question}
"""
    response_text = provider.generate_content(prompt)
    return {"answer": response_text}


def rag_add_paper(paper_name: str, text: str) -> dict:
    """Add a paper to the RAG library."""
    from utils.rag_utils import add_paper_to_library
    return add_paper_to_library(paper_name, text)
