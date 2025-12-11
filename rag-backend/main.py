from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import asyncio
import logging
from datetime import datetime

# Import from local modules
from config import settings
from database import get_db_connection
from document_processor import document_processor  # Import the global document processor instance
from config import settings

# Initialize the FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation Chatbot for the AI-Humanaid Textbook",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize document processor (which includes DB and vector store) on startup"""
    logger.info("Initializing RAG Chatbot API...")

    # Initialize database and vector store via the document processor
    await document_processor.db.connect()
    await document_processor.vector_store.init()

    logger.info("RAG Chatbot API initialized successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG Chatbot API is running", "status": "healthy"}

# Include API routes
from api.documents import router as documents_router
from api.chat import router as chat_router

app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)