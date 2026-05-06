"""Qdrant client wrapper for vector storage and retrieval."""
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

from src.config import settings


class QdrantClientWrapper:
    """Wrapper for Qdrant vector operations."""

    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection_name = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure collection exists with proper schema."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # Standard embedding size
                    distance=Distance.COSINE,
                ),
            )

    def index_report(
        self,
        report_id: str,
        session_id: str,
        company: str,
        position: str,
        content: str,
        chunk_size: int = 500,
    ):
        """Index a report into Qdrant.

        Args:
            report_id: Unique report identifier
            session_id: Session this report belongs to
            company: Company name
            position: Position name
            content: Full report content
            chunk_size: Approximate characters per chunk
        """
        # Split content into chunks (simple character-based splitting)
        chunks = self._split_into_chunks(content, chunk_size)

        points = []
        for i, chunk in enumerate(chunks):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=self._get_dummy_vector(),  # Placeholder - real implementation needs embedding model
                payload={
                    "report_id": report_id,
                    "session_id": session_id,
                    "company": company,
                    "position": position,
                    "chunk_index": i,
                    "content": chunk,
                },
            )
            points.append(point)

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        company: Optional[str] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Search for relevant report chunks.

        Args:
            query: Search query
            session_id: Optional session filter
            company: Optional company filter
            top_k: Number of results to return

        Returns:
            List of matching chunk dictionaries
        """
        # Note: Real implementation would:
        # 1. Generate query embedding using an embedding model
        # 2. Use qdrant_client.search() with the vector
        # For now, return empty list as placeholder
        return []

    def _split_into_chunks(self, content: str, chunk_size: int) -> list[str]:
        """Split content into chunks of approximately chunk_size."""
        lines = content.split("\n")
        chunks = []
        current_chunk = []

        for line in lines:
            if len("\n".join(current_chunk)) + len(line) > chunk_size:
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
            current_chunk.append(line)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _get_dummy_vector(self) -> list[float]:
        """Return a dummy vector for testing.

        Note: Real implementation should use an embedding model.
        """
        import random
        return [random.random() for _ in range(1536)]


# Singleton instance
_qdrant_client: Optional[QdrantClientWrapper] = None


def get_qdrant_client() -> QdrantClientWrapper:
    """Get or create Qdrant client singleton."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClientWrapper()
    return _qdrant_client