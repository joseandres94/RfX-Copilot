from typing import List
import openai
from ....domain.ingestion.entities.chunk import Chunk
from ....domain.shared.services.embedding_service import EmbeddingService
from ...shared.config.settings import LLMSettings

import logging
logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI embedding service"""
    def __init__(self, settings: LLMSettings):
        """Initialize OpenAI chat adapter.

        Args:
            settings: LLM configuration settings

        Raises:
            ValueError: If OpenAI API key is not provided
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self.api_key = settings.openai_api_key
        self.model = settings.openai_model_embedding

        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI()

    def create_embeddings(self, chunks: List[Chunk]) -> List[Chunk]:
        """Create embeddings for a list of chunks and return a list of chunks with the embeddings"""
        try:
            for chunk in chunks:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=chunk.content,
                    encoding_format="float",
                    )
                chunk.embedding = response.data[0].embedding
            return chunks
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise e
