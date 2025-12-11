import asyncpg
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from config import settings
from models import Document, DocumentChunk, ChatSession, ChatMessage

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Initialize connection pool"""
        if not settings.neon_database_url:
            raise ValueError("NEON_DATABASE_URL environment variable not set")

        self.pool = await asyncpg.create_pool(settings.neon_database_url)

        # Create tables if they don't exist
        await self._create_tables()

    async def _create_tables(self):
        """Create database tables if they don't exist"""
        async with self.pool.acquire() as conn:
            # Documents table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title TEXT NOT NULL,
                    source_path TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Document chunks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Chat sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Chat messages table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """)

            # Add indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_doc_id ON document_chunks(document_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)")

    async def insert_document(self, title: str, source_path: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """Insert a new document and return its ID"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "INSERT INTO documents (title, source_path, metadata) VALUES ($1, $2, $3) RETURNING id",
                title, source_path, json.dumps(metadata) if metadata else None
            )
            return str(result['id'])

    async def insert_document_chunk(self, document_id: str, content: str, chunk_index: int,
                                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Insert a document chunk and return its ID"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "INSERT INTO document_chunks (document_id, content, chunk_index, metadata) VALUES ($1, $2, $3, $4) RETURNING id",
                document_id, content, chunk_index, json.dumps(metadata) if metadata else None
            )
            return str(result['id'])

    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, document_id, content, chunk_index, metadata, created_at FROM document_chunks WHERE document_id = $1 ORDER BY chunk_index",
                document_id
            )

            chunks = []
            for row in rows:
                chunk = DocumentChunk(
                    id=str(row['id']),
                    document_id=str(row['document_id']),
                    content=row['content'],
                    chunk_index=row['chunk_index'],
                    metadata=row['metadata'],
                    created_at=row['created_at'] or datetime.utcnow()
                )
                chunks.append(chunk)

            return chunks

    async def get_document_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Get a specific document chunk by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, document_id, content, chunk_index, metadata, created_at FROM document_chunks WHERE id = $1",
                chunk_id
            )

            if not row:
                return None

            return DocumentChunk(
                id=str(row['id']),
                document_id=str(row['document_id']),
                content=row['content'],
                chunk_index=row['chunk_index'],
                metadata=row['metadata'],
                created_at=row['created_at'] or datetime.utcnow()
            )

    async def create_chat_session(self, user_id: Optional[str] = None) -> str:
        """Create a new chat session and return its ID"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "INSERT INTO chat_sessions (user_id) VALUES ($1) RETURNING id",
                user_id
            )
            return str(result['id'])

    async def add_chat_message(self, session_id: str, role: str, content: str) -> str:
        """Add a message to a chat session"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                "INSERT INTO chat_messages (session_id, role, content) VALUES ($1, $2, $3) RETURNING id",
                session_id, role, content
            )
            return str(result['id'])

    async def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, user_id, created_at FROM chat_sessions WHERE id = $1",
                session_id
            )

            if not row:
                return None

            return ChatSession(
                id=str(row['id']),
                user_id=str(row['user_id']) if row['user_id'] else None,
                created_at=row['created_at'] or datetime.utcnow()
            )

    async def get_chat_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a chat session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, session_id, role, content, timestamp FROM chat_messages WHERE session_id = $1 ORDER BY timestamp",
                session_id
            )

            messages = []
            for row in rows:
                message = ChatMessage(
                    id=str(row['id']),
                    session_id=str(row['session_id']),
                    role=row['role'],
                    content=row['content'],
                    timestamp=row['timestamp'] or datetime.utcnow()
                )
                messages.append(message)

            return messages

    async def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, title, source_path, metadata, created_at FROM documents WHERE id = $1",
                document_id
            )

            if not row:
                return None

            return Document(
                id=str(row['id']),
                title=row['title'],
                source_path=row['source_path'],
                metadata=row['metadata'],
                created_at=row['created_at'] or datetime.utcnow()
            )

# Global database instance
db_manager = DatabaseManager()

async def get_db_connection():
    """Dependency for FastAPI to get database connection"""
    if not db_manager.pool:
        await db_manager.connect()
    return db_manager