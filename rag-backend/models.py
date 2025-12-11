from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

# Document-related models
class DocumentBase(BaseModel):
    title: str
    source_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    content: str

class Document(DocumentBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentChunkBase(BaseModel):
    document_id: str
    content: str
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None

class DocumentChunkCreate(DocumentChunkBase):
    embedding: Optional[List[float]] = None

class DocumentChunk(DocumentChunkBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Chat-related models
class ChatSessionBase(BaseModel):
    user_id: Optional[str] = None

class ChatSession(ChatSessionBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True

# API request/response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    top_k: int = 5

class QueryWithContextRequest(BaseModel):
    query: str
    context: str
    session_id: Optional[str] = None
    top_k: int = 5

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    session_id: str

class DocumentIndexRequest(BaseModel):
    title: str
    content: str
    source_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentIndexResponse(BaseModel):
    document_id: str
    chunks_indexed: int
    status: str