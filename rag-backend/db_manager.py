# database.py or db_manager.py
import asyncpg
from config import settings

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(dsn=settings.neon_database_url)
            print("✅ Database connected")

    async def insert_document(self, title, source_path=None, metadata=None):
        if self.pool is None:
            raise Exception("Database not connected. Call connect() first.")
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    source_path TEXT,
                    metadata JSONB
                )
                """
            )
            result = await conn.fetchrow(
                """
                INSERT INTO documents(title, source_path, metadata)
                VALUES($1, $2, $3) RETURNING id
                """,
                title, source_path, metadata
            )
            return result["id"]

    async def insert_document_chunk(self, document_id, content, chunk_index, metadata=None):
        if self.pool is None:
            raise Exception("Database not connected. Call connect() first.")
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id),
                    chunk_index INT,
                    content TEXT,
                    metadata JSONB
                )
                """
            )
            result = await conn.fetchrow(
                """
                INSERT INTO document_chunks(document_id, chunk_index, content, metadata)
                VALUES($1, $2, $3, $4) RETURNING id
                """,
                document_id, chunk_index, content, metadata
            )
            return result["id"]
