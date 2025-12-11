from fastapi import APIRouter, HTTPException, Depends
from typing import List
import json
from models import DocumentIndexRequest, DocumentIndexResponse, Document
from database import get_db_connection
from document_processor import document_processor

router = APIRouter()

@router.post("/index", response_model=DocumentIndexResponse)
async def index_document(request: DocumentIndexRequest, db=Depends(get_db_connection)):
    """
    Index a new document by chunking it, generating embeddings, and storing in vector database
    """
    try:
        document_id = await document_processor.process_and_store_document(
            title=request.title,
            content=request.content,
            source_path=request.source_path,
            metadata=request.metadata
        )
        
        # Count the number of chunks for this document
        chunks = await db.get_document_chunks(document_id)
        
        return DocumentIndexResponse(
            document_id=document_id,
            chunks_indexed=len(chunks),
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing document: {str(e)}")

@router.get("/list", response_model=List[Document])
async def list_documents(db=Depends(get_db_connection)):
    """
    List all indexed documents
    """
    try:
        # Execute raw SQL query to fetch all documents
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, title, source_path, metadata, created_at FROM documents ORDER BY created_at DESC"
            )

            documents = []
            for row in rows:
                # The metadata column may be stored as JSON text in the DB.
                # Try to parse it into a dict for the Pydantic model.
                raw_meta = row.get('metadata')
                parsed_meta = None
                if isinstance(raw_meta, str):
                    try:
                        import json
                        parsed_meta = json.loads(raw_meta)
                    except Exception:
                        parsed_meta = raw_meta
                else:
                    parsed_meta = raw_meta

                document = Document(
                    id=str(row['id']),
                    title=row['title'],
                    source_path=row['source_path'],
                    metadata=parsed_meta,
                    created_at=row['created_at']
                )
                documents.append(document)

            return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str, db=Depends(get_db_connection)):
    """
    Get a specific document by ID
    """
    try:
        document = await db.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")