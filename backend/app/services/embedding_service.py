from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using SentenceTransformers"""

    def __init__(self):
        """Initialize the embedding model"""
        self.model_name = settings.EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info(
    f"Model loaded successfully. Dimension: {
        settings.VECTOR_DIMENSIONS}"  
)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a given text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)

        # Convert to list for database storage
        return embedding.tolist()

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Generate embeddings in batch (more efficient)
        embeddings = self.model.encode(
            texts, convert_to_numpy=True, batch_size=32)

        return embeddings.tolist()

    def compute_similarity(
            self,
            embedding1: List[float],
            embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Compute cosine similarity
        similarity = np.dot(vec1, vec2) / \
            (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        return float(similarity)
