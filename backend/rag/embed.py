import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# Load sentence transformer model globally/lazily
# We use 'all-MiniLM-L6-v2' as it is fast, lightweight, and runs perfectly on CPU
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def create_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generates sentence-transformer embeddings for a list of texts.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.astype('float32')

def build_faiss_index(chunks: List[str]) -> Tuple[faiss.Index, List[str]]:
    """
    Creates a FAISS IndexFlatL2 index from text chunks and returns the index along with chunks.
    """
    if not chunks:
        # Create an empty index
        index = faiss.IndexFlatL2(384)
        return index, []
        
    embeddings = create_embeddings(chunks)
    dimension = embeddings.shape[1]
    
    # We use a simple flat L2 index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    return index, chunks
