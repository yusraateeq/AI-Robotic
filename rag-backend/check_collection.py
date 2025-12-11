#!/usr/bin/env python3
import asyncio
from qdrant_client import AsyncQdrantClient
from config import settings

async def main():
    client = AsyncQdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )
    
    try:
        collections = await client.get_collections()
        print("Collections:")
        for collection in collections.collections:
            print(f"  - {collection.name}")
        
        # Check textbook_chunks specifically
        collection_info = await client.get_collection("textbook_chunks")
        print(f"\ntextbook_chunks collection:")
        print(f"  Points count: {collection_info.points_count}")
        print(f"  Vector size: {collection_info.config.params.vectors.size if collection_info.config.params.vectors else 'N/A'}")
        
        # Try to get a few points
        points = await client.scroll(
            collection_name="textbook_chunks",
            limit=3
        )
        print(f"\nFirst 3 points:")
        for i, point in enumerate(points[0]):
            print(f"  Point {i+1}:")
            print(f"    ID: {point.id}")
            print(f"    Payload keys: {list(point.payload.keys()) if point.payload else 'None'}")
            if point.payload:
                print(f"    Content preview: {str(point.payload.get('content', ''))[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

asyncio.run(main())
