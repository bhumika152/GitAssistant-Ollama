"""
Local embeddings using Ollama
"""
import requests
import numpy as np
from typing import List
from config.settings import Settings
from utils.logger import logger


class EmbeddingsGenerator:
    """Generate embeddings using Ollama"""

    def __init__(self):
        self.model = Settings.EMBEDDING_MODEL
        self.url = Settings.OLLAMA_BASE_URL + "/api/embeddings"

        logger.info(f"🦙 Using Ollama embedding model: {self.model}")

        # Test connection
        try:
            _ = self.generate_query_embedding("test")
            logger.info("✅ Ollama embeddings ready")
        except Exception as e:
            logger.error("❌ Ollama is not running or model missing")
            raise e

    def _embed(self, text: str) -> List[float]:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": text,
            },
            timeout=60,
        )

        if response.status_code != 200:
            raise RuntimeError(response.text)

        return response.json()["embedding"]

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        logger.info(f"Generating embeddings for {len(texts)} documents (Ollama)...")
        embeddings = [self._embed(text) for text in texts]
        return np.array(embeddings, dtype=np.float32)

    def generate_query_embedding(self, query: str) -> np.ndarray:
        return np.array(self._embed(query), dtype=np.float32)

    def __call__(self, texts: List[str]) -> List[List[float]]:
        return self.generate_embeddings(texts).tolist()
