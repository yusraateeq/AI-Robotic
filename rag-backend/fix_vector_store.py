"""
Script to fix the Qdrant vector store collection to match the correct embedding dimensions
"""
import asyncio
import os
import sys

# Add the parent directory to the path so we can import from the rag-backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from vector_store import VectorStore

async def fix_vector_store():
    """
    Fix the Qdrant collection by deleting and recreating with correct dimensions
    """
    print("🔧 Connecting to Qdrant...")
    vector_store = VectorStore()
    
    # Initialize the client
    await vector_store.init()
    
    print(f"🔍 Checking collection: {vector_store.collection_name}")
    
    try:
        # Get collection info
        collection_info = vector_store.client.get_collection(vector_store.collection_name)
        print(f"📦 Collection '{vector_store.collection_name}' exists with vector size: {collection_info.config.params.vectors.size}")
        
        # Generate a sample embedding to check actual size
        print(f"🔍 Checking actual embedding size for model: {settings.embedding_model}")
        sample_text = "This is a sample text for testing embedding dimensions."
        sample_embedding = await vector_store.generate_embedding(sample_text)
        actual_size = len(sample_embedding)
        print(f"📊 Actual embedding size: {actual_size}")
        
        if collection_info.config.params.vectors.size != actual_size:
            print(f"❌ Dimension mismatch detected! Collection has {collection_info.config.params.vectors.size} but embeddings have {actual_size}")
            print("🔄 Recreating collection with correct dimensions...")
            
            # Drop the existing collection
            vector_store.client.delete_collection(vector_store.collection_name)
            print(f"🗑️  Deleted collection: {vector_store.collection_name}")
            
            # Recreate with correct dimensions
            vector_store.client.create_collection(
                collection_name=vector_store.collection_name,
                vectors_config={
                    "size": actual_size,
                    "distance": "Cosine"
                }
            )
            print(f"✅ Created collection: {vector_store.collection_name} with vector size: {actual_size}")
        else:
            print("✅ Dimensions match, no need to recreate collection")
            
    except Exception as e:
        print(f"⚠️  Collection doesn't exist or error checking: {e}")
        print(f"🔧 Creating new collection with correct dimensions for model: {settings.embedding_model}")
        
        # Determine embedding size based on the model being used
        if "text-embedding-3-large" in settings.embedding_model:
            vector_size = 3072
        elif "text-embedding-3-small" in settings.embedding_model:
            vector_size = 1536
        elif "ada" in settings.embedding_model:
            vector_size = 1536
        else:
            # Default to 1536 for older models or if model name is not recognized
            vector_size = 1536
        
        # Create collection with correct vector configuration
        vector_store.client.create_collection(
            collection_name=vector_store.collection_name,
            vectors_config={
                "size": vector_size,
                "distance": "Cosine"
            }
        )
        print(f"✅ Created collection: {vector_store.collection_name} with vector size: {vector_size}")

if __name__ == "__main__":
    # Check if required environment variables are set
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    if not settings.qdrant_url:
        print("❌ Error: QDRANT_URL environment variable not set")
        exit(1)
    
    print("🔧 Fixing Qdrant vector store...")
    asyncio.run(fix_vector_store())
    print("✅ Vector store has been fixed!")