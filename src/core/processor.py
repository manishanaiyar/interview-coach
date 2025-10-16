from typing import List

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Splits a long text into smaller chunks of a specified size with overlap.

    Args:
        text: The input text to be chunked.
        chunk_size: The desired character length of each chunk.
        chunk_overlap: The number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")
    
    chunks = []
    start_index = 0
    while start_index < len(text):
        end_index = start_index + chunk_size
        chunks.append(text[start_index:end_index])
        start_index += chunk_size - chunk_overlap
        
    return chunks