"""Qdrant client wrapper for vector storage and retrieval."""
import uuid
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from src.config import settings
from src.embedding import get_embeddings


class QdrantClientWrapper:
    """Wrapper for Qdrant vector operations with real embeddings."""

    # Embedding dimension for bge-large-zh-v1.5
    EMBEDDING_SIZE = 4096

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
                    size=self.EMBEDDING_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    async def index_report(
        self,
        report_id: str,
        session_id: str,
        company: str,
        position: str,
        content: str,
        chunk_size: int = 500,
    ):
        """Index a report into Qdrant with embeddings.

        Args:
            report_id: Unique report identifier
            session_id: Session this report belongs to
            company: Company name
            position: Position name
            content: Full report content
            chunk_size: Approximate characters per chunk
        """
        embeddings = get_embeddings()

        # Split content into chunks
        chunks = self._split_into_chunks(content, chunk_size)

        # Generate embeddings for all chunks
        vectors = await embeddings.aembed_documents(chunks)

        # Create points with real vectors
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
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

    async def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        company: Optional[str] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Search for relevant report chunks using vector similarity.

        Args:
            query: Search query
            session_id: Optional session filter
            company: Optional company filter
            top_k: Number of results to return

        Returns:
            List of matching chunk dictionaries
        """
        embeddings = get_embeddings()

        # Generate query embedding
        query_vector = await embeddings.aembed_query(query)

        # Build filter if session_id or company provided
        filter_conditions = []
        if session_id:
            filter_conditions.append(
                FieldCondition(
                    key="session_id",
                    match=MatchValue(value=session_id),
                )
            )
        if company:
            filter_conditions.append(
                FieldCondition(
                    key="company",
                    match=MatchValue(value=company),
                )
            )

        search_filter = Filter(
            must=filter_conditions
        ) if filter_conditions else None

        # Search Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=top_k,
        )

        # Format results
        return [
            {
                "content": hit.payload["content"],
                "score": hit.score,
                "report_id": hit.payload["report_id"],
                "company": hit.payload["company"],
                "position": hit.payload["position"],
            }
            for hit in results
        ]

    def _split_into_chunks(self, content: str, chunk_size: int) -> list[str]:
        """Split content into chunks of approximately chunk_size."""
        lines = content.split("\n")
        chunks = []
        current_chunk = []
        current_length = 0

        for line in lines:
            line_length = len(line)
            if current_length + line_length > chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(line)
            current_length += line_length + 1  # +1 for newline

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks


# Singleton instance
_qdrant_client: Optional[QdrantClientWrapper] = None


def get_qdrant_client() -> QdrantClientWrapper:
    """Get or create Qdrant client singleton."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClientWrapper()
    return _qdrant_client