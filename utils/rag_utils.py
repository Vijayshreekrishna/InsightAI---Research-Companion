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
    """
    Split text into chunks using a recursive approach (Semantic-ish).
    Prioritizes splitting on double newlines (paragraphs), then single newlines, 
    then spaces, to avoid cutting thoughts in half.
    """
    if not text:
        return []
        
    separators = ["\n\n", "\n", " ", ""]
    final_chunks = []
    
    def _recursive_split(current_text: str, sep_idx: int) -> List[str]:
        if len(current_text) <= chunk_size:
            return [current_text]
            
        if sep_idx >= len(separators):
            return [current_text[:chunk_size]] # Hard cut if no separators left
            
        sep = separators[sep_idx]
        splits = current_text.split(sep)
        
        results = []
        current_block = ""
        
        for s in splits:
            # If adding this piece exceeds limits
            if len(current_block) + len(s) + len(sep) > chunk_size:
                if current_block:
                    results.append(current_block.strip())
                # If a single split is already too big, recurse deeper
                if len(s) > chunk_size:
                    results.extend(_recursive_split(s, sep_idx + 1))
                    current_block = ""
                else:
                    current_block = s
            else:
                current_block = (current_block + sep + s) if current_block else s
                
        if current_block:
            results.append(current_block.strip())
        return results

    # Run the recursive splitter
    raw_chunks = _recursive_split(text, 0)
    
    # Post-process for overlap and empty strings
    # (Simple overlap implementation for recursive splitting)
    # For now, we'll just return the logical blocks to keep semantic meaning high
    return [c.strip() for c in raw_chunks if c.strip()]


def is_paper_indexed(paper_name: str) -> bool:
    """Check if the paper has already been processed into the library."""
    try:
        collection = _get_collection()
        # Look for at least one chunk with this paper_name metadata
        results = collection.get(
            where={"paper_name": paper_name},
            limit=1,
            include=[]
        )
        return len(results.get("ids", [])) > 0
    except Exception:
        return False


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


def query_library(question: str, n_results: int = 5, paper_name: str = None) -> List[Dict[str, Any]]:
    """
    Semantic search across stored papers.
    If paper_name is provided, it only searches chunks belonging to that paper.
    """
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return []

        n_results = min(n_results, count)
        
        query_params = {
            "query_texts": [question],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if paper_name:
            query_params["where"] = {"paper_name": paper_name}
            
        results = collection.query(**query_params)

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
