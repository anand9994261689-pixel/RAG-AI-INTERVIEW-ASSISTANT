from typing import List

def split_text_into_chunks(text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
    """
    Splits text into overlapping chunks of a specified size.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        # Advance by chunk_size minus overlap, ensuring we make forward progress
        start += max(1, chunk_size - overlap)
        
    return chunks
