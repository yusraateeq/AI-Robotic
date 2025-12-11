import openai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct, VectorParams, Distance
from typing import List, Optional, Dict, Any
from config import settings
from models import DocumentChunk
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection_name = settings.qdrant_collection_name

    async def init(self):
        """Initialize the Qdrant client and ensure collection exists"""
        # Configure OpenAI API
        openai.api_key = settings.openai_api_key

        # Initialize Qdrant client
        if settings.qdrant_api_key:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                prefer_grpc=False
            )
        else:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                prefer_grpc=False
            )

        # Ensure collection exists
        await self._ensure_collection()

    async def _ensure_collection(self):
        """Ensure the collection exists with proper configuration"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Determine embedding size based on the model being used
                embedding_model = settings.embedding_model
                if "text-embedding-3-large" in embedding_model:
                    vector_size = 3072
                elif "text-embedding-3-small" in embedding_model:
                    vector_size = 1536
                elif "ada" in embedding_model:
                    vector_size = 1536
                else:
                    # Default to 1536 for older models or if model name is not recognized
                    vector_size = 1536

                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name} with vector size: {vector_size}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text using OpenAI API"""
        try:
            response = openai.embeddings.create(
                input=text,
                model=settings.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def store_chunk(self, chunk: DocumentChunk, embedding: Optional[List[float]] = None) -> str:
        """Store a document chunk with its embedding in Qdrant"""
        if not embedding:
            embedding = await self.generate_embedding(chunk.content)

        # Prepare payload
        payload = {
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "metadata": chunk.metadata or {}
        }

        # Store in Qdrant
        try:
            # Use the chunk ID as the point ID in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=chunk.id,  # Use the chunk's UUID as the point ID
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            return chunk.id
        except Exception as e:
            logger.error(f"Error storing chunk in Qdrant: {e}")
            raise

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks to the query"""
        try:
            # Ensure client is initialized
            if self.client is None:
                await self.init()

            # Generate embedding for the query
            query_embedding = await self.generate_embedding(query)

            # Use the HTTP API directly for reliable results
            try:
                import httpx
                url = settings.qdrant_url.rstrip('/') + f"/collections/{self.collection_name}/points/search"
                headers = {}
                if settings.qdrant_api_key:
                    headers['api-key'] = settings.qdrant_api_key

                body = {
                    "vector": query_embedding,
                    "limit": top_k,
                    "with_payload": True,
                    "with_vectors": False
                }
                resp = httpx.post(url, json=body, headers=headers, timeout=30.0)
                resp.raise_for_status()
                data = resp.json()
                search_results = data.get('result', [])
                
                # Normalize results
                results = []
                for item in search_results:
                    results.append({
                        "id": item.get('id'),
                        "score": item.get('score'),
                        "payload": item.get('payload', {})
                    })
                
                return results
            except Exception as e:
                logger.error(f"HTTP search failed: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error searching in Qdrant: {e}")
            raise

    async def delete_document_chunks(self, document_id: str):
        """Delete all chunks associated with a document"""
        try:
            # Find all chunks for this document
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        )
                    ]
                ),
                limit=10000  # Assuming we won't have more than 10k chunks per document
            )

            # Extract IDs of points to delete
            point_ids = [point.id for point in search_results[0]]

            if point_ids:
                # Delete the points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
        except Exception as e:
            logger.error(f"Error deleting document chunks from Qdrant: {e}")
            raise

# Global vector store instance
vector_store = None

def set_vector_store_instance(instance):
    """Function to set the global vector store instance from outside modules"""
    global vector_store
    vector_store = instance