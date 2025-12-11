#!/usr/bin/env python3
"""
Diagnostic script to check Qdrant client capabilities
"""
import sys
import os

# Add the parent directory to the path so we can import from the rag-backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from vector_store import VectorStore

async def check_qdrant_client():
    print("🔍 Checking Qdrant client capabilities...")
    
    # Initialize a vector store instance
    vs = VectorStore()
    
    # Initialize only the client, not the full system
    import openai
    openai.api_key = settings.openai_api_key
    
    if settings.qdrant_api_key:
        vs.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False
        )
    else:
        vs.client = QdrantClient(
            url=settings.qdrant_url,
            prefer_grpc=False
        )
    
    # Check what methods are available on the client
    print(f"Available methods on Qdrant client: {dir(vs.client)}")
    
    # Check if search method exists
    has_search = hasattr(vs.client, 'search')
    print(f"Has 'search' method: {has_search}")
    
    # Check if other potential search-related methods exist
    potential_methods = ['search', 'async_search', 'search_points', 'query']
    for method in potential_methods:
        has_method = hasattr(vs.client, method)
        print(f"Has '{method}' method: {has_method}")
    
    return has_search

if __name__ == "__main__":
    from qdrant_client import QdrantClient
    
    import asyncio
    result = asyncio.run(check_qdrant_client())
    print(f"\nSearch method available: {result}")