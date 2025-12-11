# Quick Start Guide - RAG Chatbot

## Prerequisites
- Windows 10/11 with WSL2 enabled
- Ubuntu 24.04 in WSL2
- Node.js and npm installed
- Python 3.12 with virtualenv

## One-Command Setup (For Next Time)

### Start Both Services
Create a script `start_all.sh` in the project root:
```bash
#!/bin/bash
# Terminal 1: Start Backend
(cd rag-backend && source .venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000) &

# Terminal 2: Start Frontend  
sleep 3
(cd my-website && npm start)
```

Then run:
```bash
bash start_all.sh
```

## Manual Setup (Step by Step)

### Step 1: Start Backend (in Terminal 1)
```bash
cd rag-backend
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Started server process [XXXX]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend (in Terminal 2)
```bash
cd my-website
npm start
```

**Expected Output**:
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### Step 3: Open in Browser
Visit: **http://localhost:3000**

## Testing the Chatbot

### In the Browser
1. Go to http://localhost:3000
2. Look for the RAG Chatbot component (usually a chat bubble)
3. Try asking: "What is ROS 2?"
4. See the answer with source documents

### Via API (Using curl)
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS 2?", "top_k": 3}'
```

**Expected Response**:
```json
{
  "response": "ROS 2 is a robotic middleware...",
  "sources": [...3 documents...],
  "session_id": "..."
}
```

## Troubleshooting

### Backend Won't Start
```
Error: port 8000 already in use
→ Kill existing process: wsl -d Ubuntu-24.04 -- pkill -f uvicorn
```

### Frontend Won't Start
```
Error: port 3000 already in use
→ It will automatically use 3001
→ Just access http://localhost:3001
```

### Frontend can't reach backend
```
Error: API connection refused
→ Make sure backend is running on 0.0.0.0, not 127.0.0.1
→ Check my-website/.env has: REACT_APP_API_URL=http://localhost:8000
```

### No responses from chatbot
```
→ Check that 335 documents are indexed: 
  python rag-backend/check_collection.py
→ Check backend logs for errors
```

## Key Files to Know

| File | Purpose |
|------|---------|
| `rag-backend/main.py` | FastAPI app entry point |
| `rag-backend/vector_store.py` | Qdrant search logic |
| `rag-backend/api/chat.py` | Chat endpoints |
| `my-website/.env` | Frontend API URL config |
| `rag-backend/.env` | API keys and service URLs |

## Environment Variables

### Required for Backend (`rag-backend/.env`)
- `OPENAI_API_KEY` - OpenRouter API key
- `QDRANT_URL` - Qdrant Cloud URL
- `QDRANT_API_KEY` - Qdrant API key
- `NEON_DATABASE_URL` - PostgreSQL connection
- `OPENAI_BASE_URL` - OpenRouter base URL

### Required for Frontend (`my-website/.env`)
- `REACT_APP_API_URL` - Backend URL (default: http://localhost:8000)

## Project Structure
```
project-root/
├── rag-backend/              # Python FastAPI backend
│   ├── main.py              # Entry point
│   ├── vector_store.py      # Vector search (FIXED)
│   ├── api/
│   │   └── chat.py          # Chat endpoints
│   ├── .env                 # API keys
│   └── .venv/               # Python virtual env
│
└── my-website/              # Docusaurus frontend
    ├── package.json         # npm config
    ├── .env                 # Frontend config
    └── src/components/
        └── RagChatbot/      # Chat component
```

## API Endpoints

### Health Check
```
GET /
Response: {"message":"RAG Chatbot API is running","status":"healthy"}
```

### Chat Query
```
POST /api/chat/query
Body: {
  "query": "Your question here",
  "top_k": 3,
  "session_id": "optional"
}
Response: {
  "response": "AI answer",
  "sources": [...],
  "session_id": "session-id"
}
```

### Chat with Context
```
POST /api/chat/query_with_context
Body: {
  "query": "Question",
  "context": "Selected text from page",
  "session_id": "optional"
}
```

## Performance Tips

1. **First query is slow (3-5 sec)** - Normal, it's embedding generation
2. **Subsequent queries are faster (1-2 sec)** - Embedding cache helps
3. **Response quality improves with context** - Select relevant text before asking

## Next Steps

1. ✅ Verify system is working (see Testing section)
2. ✅ Explore chatbot features (text selection, session history)
3. ✅ Add more documents to rag-backend/docs if needed
4. ✅ Customize LLM model in `rag-backend/.env`

## Support

For detailed information, see:
- `RAG_CHATBOT_COMPLETE_SOLUTION.md` - Full technical details
- `BEFORE_AFTER_COMPARISON.md` - What was fixed and why
- `RAG_CHATBOT_FIX_SUMMARY.md` - Summary of changes

---

**Ready to use! Just run: `cd rag-backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000` and then `cd my-website && npm start`**
