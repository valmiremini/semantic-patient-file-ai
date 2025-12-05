import os
import logging
from typing import List
from openai import OpenAI
import requests

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for creating embeddings from text"""

    def __init__(self):
        self.model_type = os.getenv("MODEL_TYPE", "local")

        if self.model_type == "openai":
            self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set, falling back to local embeddings")
                self.model_type = "local"
            else:
                self.client = OpenAI(api_key=api_key)
                logger.info(f"Initialized OpenAI embeddings with model: {self.embedding_model}")
                return
        elif self.model_type == "ollama":
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
            self.client = "ollama"
            logger.info(f"Initialized Ollama embeddings with model: {self.embedding_model} at {self.ollama_base_url}")
            return

        # Default: Use local sentence-transformers
        if self.model_type == "local":
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = "all-MiniLM-L6-v2"  # Fast, small model (80MB)
                logger.info(f"Loading local embedding model: {self.embedding_model}...")
                self.client = SentenceTransformer(self.embedding_model)
                logger.info(f"Successfully loaded local embedding model: {self.embedding_model}")
            except Exception as e:
                logger.error(f"Error loading local model: {str(e)}")
                logger.warning("Using dummy embeddings as fallback")
                self.client = None
                self.embedding_model = "dummy"

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        try:
            if not self.client:
                # Return dummy embedding if no client
                logger.warning("Using dummy embedding (no client configured)")
                return [0.0] * self.get_embedding_dimension()

            if self.model_type == "local":
                # Local sentence-transformers
                embedding = self.client.encode(text, convert_to_numpy=True)
                return embedding.tolist()

            elif self.client == "ollama":
                # Ollama embedding
                response = requests.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=30
                )
                response.raise_for_status()
                return response.json()["embedding"]

            else:
                # OpenAI embedding
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text
                )
                return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            # Return dummy embedding on error
            return [0.0] * self.get_embedding_dimension()

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        try:
            if not self.client:
                logger.warning("Using dummy embeddings (no client configured)")
                return [[0.0] * self.get_embedding_dimension() for _ in texts]

            if self.model_type == "local":
                # Local sentence-transformers (batch encoding)
                embeddings = self.client.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return [emb.tolist() for emb in embeddings]

            elif self.client == "ollama":
                # Ollama doesn't support batch embeddings, so we do them one by one
                embeddings = []
                for text in texts:
                    embedding = self.create_embedding(text)
                    embeddings.append(embedding)
                return embeddings

            else:
                # OpenAI batch embeddings
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=texts
                )
                return [item.embedding for item in response.data]

        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            return [[0.0] * self.get_embedding_dimension() for _ in texts]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.model_type == "local":
            # all-MiniLM-L6-v2 has 384 dimensions
            return 384
        elif self.model_type == "ollama":
            # nomic-embed-text has 768 dimensions
            return 768
        elif self.embedding_model == "text-embedding-3-small":
            return 1536
        elif self.embedding_model == "text-embedding-3-large":
            return 3072
        else:
            return 384  # Default for local models
