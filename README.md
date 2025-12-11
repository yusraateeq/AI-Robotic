# AI-Robotic

This project implements an AI-powered RAG (Retrieval-Augmented Generation) chatbot for the Humanoid Robotics textbook website.

## ✅ Features

- **Intelligent Chatbot**: Ask questions about robotics concepts and get AI-powered answers
- **Semantic Search**: Leverages vector embeddings to find relevant textbook content
- **Source Citations**: All answers include references to specific textbook sections
- **Context-Aware Queries**: Can answer questions about selected text passages
- **Cross-Platform**: Runs on WSL2 with Windows frontend access

## 🛠️ Architecture

### Backend Stack
- **FastAPI**: Modern Python web framework with async support
- **Qdrant Cloud**: Vector database for semantic search
- **Neon PostgreSQL**: Serverless database for metadata
- **OpenAI API**: Embeddings and language model integration

### Frontend Integration
- **Docusaurus**: Static site generator with React components
- **RagChatbot Component**: Embedded chat interface
- **Real-time API Communication**: Live query/response cycle

## 📊 Data Status
- **335** textbook chunks indexed
- **5** textbook chapters processed (Intro, 01-04, 06)
- **3072-dim** embedding vectors (text-embedding-3-large)
- **COSINE** distance metric for similarity search

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js/npm
- WSL2 (for Linux compatibility)
- API keys for OpenRouter, Qdrant, and Neon

### Installation
```bash
# Backend setup
cd rag-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# Frontend setup
cd ../my-website
npm install
```

### Running the System
```bash
# Terminal 1: Start backend
cd rag-backend
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend  
cd my-website
npm start
```

Then visit http://localhost:3000 to access the website with the chatbot.

## 📝 History

For detailed implementation history and technical decisions:
- See `history/rag_chatbot_implementation.md`
- See `RAG_CHATBOT_COMPLETE_SOLUTION.md`
- See `STATUS_REPORT.md`

## 🔧 Configuration

### Environment Variables
Required configuration in `rag-backend/.env`:
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
NEON_DATABASE_URL=postgresql://...
QDRANT_URL=...
QDRANT_API_KEY=...
...
```

## 🎯 Capabilities

The chatbot can answer questions about:
- ROS 2 fundamentals
- Robot kinematics
- Control systems
- Perception and navigation
- And more from the textbook content

Try asking: "What is ROS 2?" or "Explain robot kinematics"

## 🏗️ Technologies Used

- **Python 3.12**: Backend development
- **FastAPI**: API framework
- **PostgreSQL**: Metadata storage
- **Qdrant**: Vector database
- **OpenAI/GPT-3.5-turbo**: Language model
- **React 19**: Frontend component
- **Docusaurus 3.9.2**: Static site generation
- **httpx**: HTTP client
- **Pydantic**: Data validation
- **asyncio**: Asynchronous operations

## 🔍 How It Works

1. **Indexing**: Textbook content split into chunks and embedded
2. **Storage**: Vectors in Qdrant, metadata in Postgres
3. **Query**: User question converted to vector embedding
4. **Search**: Semantic search retrieves relevant chunks
5. **Generation**: LLM creates answer with source context
6. **Response**: Answer with citations returned to frontend