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
def summarize_paper(text: str):
    """Use configured LLM to summarize research paper text into sections."""
    provider = get_llm_provider()
    prompt = f"""
    You are a strict academic assistant. Summarize this research paper text in structured sections.
    
    IMPORTANT RULES:
    1. Answer ONLY using the provided text. Do not use outside knowledge.
    2. Cite the page number for every key point using [Page X] format.
    3. If the summary cannot be generated from the text, state that.

    Sections:
    - TL;DR Summary
    - Abstract Summary
    - Methodology Overview
    - Results & Findings
    - Limitations

    Return your answer as structured JSON with keys:
    tldr, abstract, methodology, results, limitations.

    Research Paper Text:
    {text[:15000]}
    """
    response_text = provider.generate_content(prompt)
    return _extract_json(response_text)


def chat_with_paper(query: str, context: str, use_general_knowledge: bool = False):
    """Ask configured LLM a question about the uploaded paper."""
    provider = get_llm_provider()
    
    if use_general_knowledge:
        prompt = f"""
        You are a helpful research assistant. You have access to the following research paper content.
        
        Answer the user's question. You may use the paper content AND your general knowledge.
        
        IMPORTANT INSTRUCTIONS:
        1. Prioritize information from the paper.
        2. If you use information from the paper, cite it with [Page X].
        3. If the answer requires outside knowledge, you may provide it, but make it clear.
        
        Paper Text:
        {context[:10000]}

        Question:
        {query}
        """
    else:
        prompt = f"""
        You are a strict research assistant. Answer the question ONLY using the provided paper text.
        If the answer is not in the text, state "I cannot find this information in the paper."
        
        IMPORTANT: Provide the page number for your answer using the format [Page X].
        Example: "The accuracy is 95% [Page 4]."

        Paper Text:
        {context[:10000]}

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

    Return JSON with keys: keywords, datasets, algorithms.
    Text:
    {text[:10000]}
    """
    response_text = provider.generate_content(prompt)
    return _extract_json(response_text)


def simplify_summary(text: str):
    """Simplify the summary for a younger audience."""
    provider = get_llm_provider()
    prompt = f"""
    Simplify this research summary as if explaining to a 15-year-old. Use short, clear sentences:
    {text[:4000]}
    """
    response_text = provider.generate_content(prompt)
    return {"simplified": response_text}


def future_research_ideas(text: str):
    """Suggest possible future research directions."""
    provider = get_llm_provider()
    prompt = f"""
    Based on this paper, suggest 3-5 possible future research directions or open problems.
    Return a numbered list.
    {text[:8000]}
    """
    response_text = provider.generate_content(prompt)
    return {"suggestions": response_text.splitlines()}


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
        return chat_with_paper(query, context, use_general_knowledge)
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
            text = text[:4500] + " ... summary truncated."

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
        {text_a[:15000]}

        --- PAPER B ---
        {text_b[:15000]}
        """

        response_text = provider.generate_content(prompt)
        return _extract_json(response_text)
