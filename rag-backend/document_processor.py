import tiktoken
from typing import List, Optional, Dict, Any
from config import settings
from models import DocumentChunkCreate, DocumentChunk
from vector_store import VectorStore
from database import DatabaseManager
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.tokenizer = tiktoken.encoding_for_model(settings.embedding_model)
        self.vector_store = VectorStore()
        self.db = DatabaseManager()

    def chunk_text(self, text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> List[str]:
        """
        Split text into chunks based on token count with overlap
        """
        # Split text into sentences to maintain semantic boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Encode the entire text to get token counts
        tokens = self.tokenizer.encode(text)

        chunks = []
        current_chunk = ""
        current_token_count = 0

        for sentence in sentences:
            sentence_tokens = self.tokenizer.encode(sentence)
            sentence_token_count = len(sentence_tokens)

            # If a single sentence is too long, split it by characters
            if sentence_token_count > max_tokens:
                # Split the long sentence into smaller pieces
                sentence_chunks = self._split_long_sentence(sentence, max_tokens)
                chunks.extend(sentence_chunks)
                continue

            # Check if adding this sentence would exceed the limit
            if current_token_count + sentence_token_count > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())

                # Add overlap by including some tokens from the previous chunk
                if overlap_tokens > 0:
                    # Get the last part of the current chunk as overlap
                    overlap_tokens_text = self._get_overlap_text(current_chunk, overlap_tokens)
                    current_chunk = overlap_tokens_text + " " + sentence
                    current_token_count = len(self.tokenizer.encode(current_chunk))
                else:
                    current_chunk = sentence
                    current_token_count = sentence_token_count
            else:
                current_chunk += " " + sentence
                current_token_count += sentence_token_count

        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split_long_sentence(self, sentence: str, max_tokens: int) -> List[str]:
        """
        Split a long sentence into smaller chunks based on token count
        """
        words = sentence.split()
        chunks = []
        current_chunk = ""
        current_token_count = 0

        for word in words:
            word_tokens = self.tokenizer.encode(word)
            word_token_count = len(word_tokens)

            if current_token_count + word_token_count > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = word
                current_token_count = word_token_count
            else:
                if current_chunk:
                    current_chunk += " " + word
                else:
                    current_chunk = word
                current_token_count += word_token_count

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap_text(self, text: str, num_tokens: int) -> str:
        """
        Get the last few tokens worth of text from the given text
        """
        tokens = self.tokenizer.encode(text)
        # Take the last num_tokens tokens
        tokens_to_take = tokens[-num_tokens:] if len(tokens) > num_tokens else tokens
        # Decode back to text
        return self.tokenizer.decode(tokens_to_take)

    async def process_and_store_document(self, title: str, content: str,
                                       source_path: Optional[str] = None,
                                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a document by chunking it, generating embeddings, and storing in both vector store and database
        """
        logger.info(f"Processing document: {title}")

        # Chunk the document content
        chunks = self.chunk_text(content)
        logger.info(f"Document chunked into {len(chunks)} chunks")

        # Insert document record in database
        document_id = await self.db.insert_document(title, source_path, metadata)

        # Process each chunk
        for i, chunk_content in enumerate(chunks):
            # Create document chunk record in database
            chunk = DocumentChunkCreate(
                document_id=document_id,
                content=chunk_content,
                chunk_index=i
            )

            # Store in database first
            chunk_id = await self.db.insert_document_chunk(
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                metadata=chunk.metadata
            )

            # Generate and store embedding in vector store
            embedding = await self.vector_store.generate_embedding(chunk_content)
            await self.vector_store.store_chunk(
                DocumentChunk(
                    id=chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    metadata=chunk.metadata,
                    created_at=datetime.utcnow()
                ),
                embedding
            )

        logger.info(f"Document {title} processed and stored with ID: {document_id}")
        return document_id

# Global document processor instance
document_processor = DocumentProcessor()