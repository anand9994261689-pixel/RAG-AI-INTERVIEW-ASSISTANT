import faiss
import numpy as np
from typing import List
from backend.rag.embed import get_embedding_model

def retrieve_chunks(query: str, index: faiss.Index, chunks: List[str], k: int = 3) -> List[str]:
    """
    Search FAISS index and return the top k relevant chunks for the query.
    """
    if not chunks or index is None or index.ntotal == 0:
        return []
        
    # Generate query embedding
    model = get_embedding_model()
    query_emb = model.encode([query], convert_to_numpy=True).astype('float32')
    
    # Search the FAISS index
    k = min(k, len(chunks))
    distances, indices = index.search(query_emb, k)
    
    retrieved = []
    for idx in indices[0]:
        if idx != -1 and idx < len(chunks):
            retrieved.append(chunks[idx])
            
    return retrieved

def retrieve_context(query: str, index: faiss.Index, chunks: List[str], k: int = 3) -> str:
    """
    Search FAISS index and return the combined text block as context.
    """
    matched_chunks = retrieve_chunks(query, index, chunks, k)
    return "\n\n---\n\n".join(matched_chunks)
