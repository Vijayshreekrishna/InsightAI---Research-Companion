# utils/rag_utils.py
"""
Local Insights Library – Semantic RAG Module
Uses ChromaDB + sentence-transformers (all-MiniLM-L6-v2) for persistent
vector storage. Works fully offline after first model download (~90 MB).
"""

import os
import re
from typing import List, Dict, Any

# Lazy imports to avoid startup cost if not used
_chroma_client = None
_collection = None
_embedding_fn = None

LIBRARY_PATH = "./insights_library"
COLLECTION_NAME = "research_papers"
CHUNK_SIZE = 600       # chars per chunk
CHUNK_OVERLAP = 100    # overlap between chunks


def _get_embedding_function():
    """Lazily load sentence-transformers embedding function."""
    global _embedding_fn
    if _embedding_fn is None:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        _embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _embedding_fn


def _get_collection():
    """Lazily initialise ChromaDB client and collection."""
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=LIBRARY_PATH)
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=_get_embedding_function(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def add_paper_to_library(paper_name: str, text: str) -> Dict[str, Any]:
    """
    Chunk, embed and store a paper in ChromaDB.
    Returns a dict with status and number of chunks added.
    """
    try:
        collection = _get_collection()
        chunks = _chunk_text(text)

        # Build safe document IDs (strip non-alphanumeric chars)
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", paper_name)

        ids = [f"{safe_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"paper_name": paper_name, "chunk_index": i} for i in range(len(chunks))]

        # Upsert so re-uploading the same paper doesn't duplicate
        collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)

        return {
            "status": "success",
            "paper_name": paper_name,
            "chunks_added": len(chunks),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def query_library(question: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic search across all stored papers.
    Returns list of dicts with 'text', 'paper_name', 'chunk_index', 'distance'.
    """
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return []

        n_results = min(n_results, count)
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            hits.append({
                "text": doc,
                "paper_name": meta.get("paper_name", "Unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "distance": round(dist, 4),
            })
        return hits
    except Exception as e:
        return []


def get_library_stats() -> Dict[str, Any]:
    """Return info about all papers currently in the library."""
    try:
        collection = _get_collection()
        total_chunks = collection.count()
        if total_chunks == 0:
            return {"total_chunks": 0, "papers": []}

        # Get unique paper names from metadata
        all_meta = collection.get(include=["metadatas"])["metadatas"]
        paper_names = sorted(set(m.get("paper_name", "Unknown") for m in all_meta))

        return {
            "total_chunks": total_chunks,
            "papers": paper_names,
        }
    except Exception as e:
        return {"total_chunks": 0, "papers": [], "error": str(e)}


def delete_paper_from_library(paper_name: str) -> Dict[str, Any]:
    """Remove all chunks for a given paper from the library."""
    try:
        collection = _get_collection()
        results = collection.get(where={"paper_name": paper_name})
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return {"status": "success", "deleted_chunks": len(ids)}
    except Exception as e:
        return {"status": "error", "error": str(e)}
