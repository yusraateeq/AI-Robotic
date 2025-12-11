import asyncio, json, httpx
from document_processor import document_processor
from config import settings

async def run():
    emb = await document_processor.vector_store.generate_embedding("digital twin simulation")
    print("embedding len", len(emb))
    url = settings.qdrant_url.rstrip('/') + f"/collections/{document_processor.vector_store.collection_name}/points/search"
    headers = {}
    if settings.qdrant_api_key:
        headers['api-key']=settings.qdrant_api_key
    body = {'vector': emb, 'limit': 5, 'with_payload': True}
    r = httpx.post(url, json=body, headers=headers, timeout=20.0)
    print('HTTP', r.status_code)
    print(json.dumps(r.json(), indent=2))

if __name__ == '__main__':
    asyncio.run(run())
