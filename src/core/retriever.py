import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class Retriever:
    """
    A retriever class that uses SentenceTransformers and FAISS for
    building a searchable index and retrieving relevant text chunks.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the Retriever by loading the sentence transformer model.
        """
        # Load a pre-trained model for creating embeddings
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.text_chunks = []

    def build_index(self, text_chunks: List[str]):
        """
        Builds a FAISS index from a list of text chunks.

        Args:
            text_chunks: A list of strings to be indexed.
        """
        self.text_chunks = text_chunks
        # Convert text chunks to vector embeddings
        embeddings = self.model.encode(text_chunks, convert_to_tensor=False)
        
        # Get the dimension of the embeddings
        d = embeddings.shape[1]
        
        # Build the FAISS index
        self.index = faiss.IndexFlatL2(d)
        self.index.add(np.array(embeddings, dtype=np.float32))

    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Searches the index for the most relevant text chunks for a given query.

        Args:
            query: The user's query string.
            k: The number of top results to return.

        Returns:
            A list of the top k most relevant text chunks.
        """
        if self.index is None:
            raise RuntimeError("Index has not been built yet. Please call build_index() first.")
        
        # Convert the query to a vector embedding
        query_embedding = self.model.encode([query])
        
        # Search the FAISS index for the k nearest neighbors
        distances, indices = self.index.search(np.array(query_embedding, dtype=np.float32), k)
        
        # Return the actual text chunks corresponding to the top indices
        return [self.text_chunks[i] for i in indices[0]]