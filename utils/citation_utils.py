# utils/citation_utils.py
"""
Citation Influence Graph – OpenAlex API integration.
OpenAlex is completely free and requires no API key.
Docs: https://docs.openalex.org
"""

import requests
from typing import Optional, Dict, Any, List

OPENALEX_BASE = "https://api.openalex.org"
HEADERS = {"User-Agent": "InsightAI/1.0 (research-companion)"}


def search_paper_openalex(title: str) -> Optional[Dict[str, Any]]:
    """
    Search OpenAlex for a paper by title. Returns the best matching work dict.
    """
    try:
        url = f"{OPENALEX_BASE}/works"
        params = {
            "search": title,
            "per-page": 5,
            "select": "id,title,doi,publication_year,cited_by_count,authorships,referenced_works",
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None
        # Return the first (most relevant) result
        return results[0]
    except Exception as e:
        return {"error": str(e)}


def get_work_details(work_id: str) -> Dict[str, Any]:
    """
    Fetch full details for an OpenAlex work ID (e.g. 'W2741809807').
    """
    try:
        # Normalise ID – strip URL prefix if present
        if work_id.startswith("https://openalex.org/"):
            work_id = work_id.split("/")[-1]
        url = f"{OPENALEX_BASE}/works/{work_id}"
        params = {
            "select": "id,title,doi,publication_year,cited_by_count,authorships,referenced_works,abstract_inverted_index"
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def get_citation_network(
    work_id: str,
    max_references: int = 20,
) -> Dict[str, Any]:
    """
    Build a citation graph for the given OpenAlex work ID.
    Returns:
      - nodes: list of {id, title, year, citations}
      - edges: list of {source, target}
      - root_id: the input paper's ID
    """
    nodes: Dict[str, Dict] = {}
    edges: List[Dict] = []

    # Normalise root ID
    if work_id.startswith("https://openalex.org/"):
        root_id = work_id.split("/")[-1]
    else:
        root_id = work_id

    # --- Fetch root paper ---
    root = get_work_details(root_id)
    if "error" in root:
        return {"error": root.get("error", "Could not fetch root paper"), "nodes": [], "edges": []}

    def _short_id(full_id: str) -> str:
        return full_id.split("/")[-1] if "/" in full_id else full_id

    def _first_author(work: dict) -> str:
        auths = work.get("authorships", [])
        if isinstance(auths, list) and len(auths) > 0:
            first_auth = auths[0]
            if isinstance(first_auth, dict) and isinstance(first_auth.get("author"), dict):
                return str(first_auth["author"].get("display_name", "Unknown"))
        return "Unknown"

    root_short = _short_id(root.get("id", root_id))
    nodes[root_short] = {
        "id": root_short,
        "title": root.get("title", "Unknown Title"),
        "year": root.get("publication_year", "N/A"),
        "citations": root.get("cited_by_count", 0),
        "author": _first_author(root),
        "doi": root.get("doi", ""),
        "is_root": True,
    }

    # --- Fetch referenced works (the papers THIS paper cites) ---
    referenced_ids = root.get("referenced_works", [])[:max_references]

    if referenced_ids:
        # Batch fetch referenced works
        ids_filter = "|".join([_short_id(r) for r in referenced_ids])
        try:
            url = f"{OPENALEX_BASE}/works"
            params = {
                "filter": f"openalex:{ids_filter}",
                "per-page": max_references,
                "select": "id,title,publication_year,cited_by_count,authorships,doi",
            }
            resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            ref_works = resp.json().get("results", [])
        except Exception:
            ref_works = []

        for w in ref_works:
            if not isinstance(w, dict):
                continue
            sid = _short_id(w.get("id", ""))
            if not sid:
                continue
            nodes[sid] = {
                "id": sid,
                "title": w.get("title", "Unknown"),
                "year": w.get("publication_year", "N/A"),
                "citations": w.get("cited_by_count", 0),
                "author": _first_author(w),
                "doi": w.get("doi", ""),
                "is_root": False,
            }
            edges.append({"source": root_short, "target": sid, "label": "cites"})

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "root_id": root_short,
    }


def format_authors(work: dict) -> str:
    """Return first 3 author display names as a string."""
    auths = work.get("authorships", [])
    if not isinstance(auths, list):
        return "Unknown"
        
    names = []
    for i, a in enumerate(auths):
        if i >= 3:
            break
        if isinstance(a, dict) and isinstance(a.get("author"), dict):
            names.append(str(a["author"].get("display_name", "Unknown")))
            
    result = ", ".join(names)
    if len(auths) > 3:
        result += " et al."
    return result
