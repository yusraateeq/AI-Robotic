# RAG Chatbot for AI-Humanaid Textbook

This project implements a Retrieval-Augmented Generation (RAG) chatbot for the AI-Humanaid textbook. The system allows students to ask questions about the textbook content and get AI-powered responses based only on the provided material.

## Architecture

The system consists of:

- **FastAPI Backend**: Handles document processing, indexing, and chat functionality
- **Qdrant Vector Store**: Stores document embeddings for semantic search
- **Neon Postgres**: Stores document metadata and chat history
- **OpenAI API**: Generates responses using retrieved context
- **Docusaurus Frontend**: Textbook website with integrated chatbot UI

## Prerequisites

- Python 3.8+
- Node.js 16+ (for the Docusaurus frontend)
- OpenAI API key
- Qdrant Cloud account (or local instance)
- Neon Serverless Postgres database

## Setup

### 1. Backend Setup

```bash
# Navigate to the rag-backend directory
cd rag-backend/

# Install Python dependencies
pip install -r requirements.txt

# Create a .env file with your API keys:
```

```env
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here  # if using cloud
QDRANT_COLLECTION_NAME=textbook_chunks
NEON_DATABASE_URL=your_neon_database_url_here
DEBUG=true
```

### 2. Frontend Setup

```bash
# Navigate to the my-website directory
cd ../my-website/

# Install Node.js dependencies
npm install

# Create .env file for frontend:
```

```env
REACT_APP_API_URL=http://localhost:8000  # URL of your running backend
```

### 3. Index Textbook Content

First, start the backend server:

```bash
cd ../rag-backend/
uvicorn main:app --reload
```

Then, run the script to load the textbook chapters:

```bash
python load_textbook_content.py
```

### 4. Run the Applications

Start the backend:

```bash
cd rag-backend/
uvicorn main:app --host 0.0.0.0 --port 8000
```

In a new terminal, start the Docusaurus frontend:

```bash
cd my-website/
npm run start
```

## Testing

To test the system, run the test script:

```bash
cd rag-backend/
python test_rag_system.py
```

This will verify that all components are working together correctly.

## Features

- **Question Answering**: Ask questions about textbook content
- **Context-Aware Queries**: Select text on the page and ask questions about it
- **Source Attribution**: Responses include references to source documents
- **Chat History**: Conversations are saved per session
- **Responsive UI**: Works on desktop and mobile devices

## API Endpoints

### Documents
- `POST /api/documents/index` - Index a new document
- `GET /api/documents/list` - List indexed documents
- `GET /api/documents/{id}` - Get a specific document

### Chat
- `POST /api/chat/query` - Submit a chat query
- `POST /api/chat/query_with_context` - Submit query with selected text
- `GET /api/chat/history/{session_id}` - Get chat history

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_URL` - URL to your Qdrant instance
- `QDRANT_API_KEY` - Qdrant API key (if using cloud)
- `QDRANT_COLLECTION_NAME` - Name of the Qdrant collection
- `NEON_DATABASE_URL` - Connection string for Neon Postgres
- `DEBUG` - Set to "true" for debug mode
- `REACT_APP_API_URL` - Backend API URL for frontend (in frontend .env)

## Technologies Used

- **Backend**: FastAPI, Python, asyncpg
- **Vector Store**: Qdrant Cloud
- **Database**: Neon Serverless Postgres
- **AI**: OpenAI API for embeddings and chat
- **Frontend**: React, Docusaurus
- **Text Processing**: Tiktoken, Pydantic