"""
RAG retriever using ChromaDB with Ollama (nomic-embed-text) embeddings

"""
import os
# ✅ MUST be before any chromadb import
os.environ["CHROMA_DISABLE_ONNX"] = "1"
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Tuple
from core.code_parser import CodeDocument
from core.embeddings import EmbeddingsGenerator
from config.settings import Settings
from utils.logger import logger


class RAGRetriever:
    """Retrieve relevant code documents using ChromaDB"""

    def __init__(self):
        self.embeddings_generator = EmbeddingsGenerator()
        self.chroma_client = None
        self.collection = None
        self.documents = []

        # Setup ChromaDB storage path
        self.db_path = Settings.CHROMADB_DIR
        self.db_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"ChromaDB path: {self.db_path}")

    def _get_collection_name(self, repo_name: str) -> str:
        """Generate valid collection name from repository name"""
        name = f"repo_{repo_name}".replace("-", "_").replace(".", "_")
        name = "".join(c for c in name if c.isalnum() or c in "_-.")
        return name[:63].lower()

    def _init_client(self, collection_name: str):
        """Initialize ChromaDB client and collection"""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            logger.info("✅ ChromaDB client initialized")

            # 🔥 CRITICAL FIX: ALWAYS pass embedding_function
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embeddings_generator,
                metadata={"description": "GitHub repository code embeddings"},
            )

            logger.info(f"✅ Collection ready: {collection_name}")

        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise

    def collection_exists(self, collection_name: str) -> bool:
        try:
            if not self.collection:
                self._init_client(collection_name)
            return self.collection.count() > 0
        except Exception:
            return False

    def build_index(self, documents: List[CodeDocument], repo_name: str):
        if not documents:
            raise ValueError("No documents provided for indexing")

        collection_name = self._get_collection_name(repo_name)
        self._init_client(collection_name)

        existing_count = self.collection.count()
        if existing_count > 0:
            logger.info(
                f"Collection '{collection_name}' already has {existing_count} documents"
            )
            self.documents = documents
            return

        logger.info(f"Building index with {len(documents)} documents...")
        self.documents = documents

        ids, contents, metadatas = [], [], []

        for idx, doc in enumerate(documents):
            ids.append(f"doc_{idx}")
            contents.append(doc.content)
            metadatas.append(
                {
                    "file_path": doc.file_path,
                    "language": doc.language,
                    "chunk_id": doc.chunk_id,
                }
            )

        logger.info("Generating embeddings...")
        embeddings = self.embeddings_generator.generate_embeddings(contents)

        batch_size = 500
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            self.collection.add(
                ids=ids[i:end],
                documents=contents[i:end],
                metadatas=metadatas[i:end],
                embeddings=embeddings[i:end].tolist(),
            )

        logger.info("✅ Index built successfully")

    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[CodeDocument, float]]:
        if not self.collection:
            raise ValueError("Collection not initialized")

        top_k = top_k or Settings.TOP_K_RESULTS

        query_embedding = self.embeddings_generator.generate_query_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            similarity = max(0.0, min(1.0, 1 - (dist**2 / 2)))
            retrieved.append(
                (
                    CodeDocument(
                        content=text,
                        file_path=meta["file_path"],
                        language=meta["language"],
                        chunk_id=meta["chunk_id"],
                    ),
                    similarity,
                )
            )

        return retrieved

    def get_context_for_query(self, query: str, top_k: int = None) -> str:
        results = self.retrieve(query, top_k)
        return "\n\n".join(
            f"--- Document {i+1} (Score: {score:.3f}) ---\n{doc.content}"
            for i, (doc, score) in enumerate(results)
        )
