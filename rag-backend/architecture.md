# RAG Chatbot Architecture

## Overview
The RAG (Retrieval-Augmented Generation) chatbot will be built using FastAPI as the backend, with Qdrant Cloud for vector storage, Neon Serverless Postgres for metadata, and OpenAI for chat capabilities. The system will be integrated with a Docusaurus-based textbook website.

## Components

### 1. FastAPI Backend
- Serves as the main API layer
- Handles document processing and indexing
- Manages chat queries and responses
- Integrates with vector database (Qdrant) and metadata database (Neon)

### 2. Document Processing Module
- Processes textbook content (chapters) into chunks
- Generates embeddings for each chunk
- Stores metadata in Neon Postgres
- Stores vector embeddings in Qdrant

### 3. Qdrant Vector Database
- Stores document embeddings for semantic search
- Enables similarity search for relevant context
- Free tier compatible

### 4. Neon Serverless Postgres
- Stores document metadata (source, chapter, section, etc.)
- Stores user queries and conversation history
- Tracks document-chunk relationships

### 5. OpenAI Integration
- Uses OpenAI API for generating responses
- Implements RAG pattern by providing context from retrieved documents
- Supports context-aware responses

### 6. Frontend Integration
- Chatbot UI embedded in Docusaurus site
- Text selection functionality for context-aware queries
- Real-time chat interface

## Data Flow

### Indexing Process
1. Textbook content is processed into chunks
2. Embeddings generated using OpenAI's embedding API
3. Vector embeddings stored in Qdrant
4. Metadata stored in Neon Postgres (chunk_id, source, chapter, etc.)

### Query Process
1. User submits query through frontend
2. Query embedding generated using OpenAI API
3. Similarity search performed in Qdrant to find relevant chunks
4. Relevant chunks retrieved from Qdrant along with metadata from Neon Postgres
5. Context assembled from retrieved chunks
6. OpenAI API called with context and user query to generate response
7. Response returned to frontend

## API Endpoints

### Document Management
- `POST /api/documents/index` - Index new document
- `GET /api/documents/list` - List indexed documents

### Chat Functionality
- `POST /api/chat/query` - Submit a chat query
- `POST /api/chat/query_with_context` - Submit a query with selected text context
- `GET /api/chat/history/{user_id}` - Retrieve chat history

## Database Schema

### Neon Postgres Tables

#### documents
- id (UUID, primary key)
- title (VARCHAR)
- source_path (VARCHAR)
- created_at (TIMESTAMP)

#### document_chunks
- id (UUID, primary key)
- document_id (UUID, foreign key)
- content (TEXT)
- chunk_index (INTEGER)
- metadata (JSONB)
- created_at (TIMESTAMP)

#### chat_sessions
- id (UUID, primary key)
- user_id (UUID)
- created_at (TIMESTAMP)

#### chat_messages
- id (UUID, primary key)
- session_id (UUID, foreign key)
- role (VARCHAR - 'user' or 'assistant')
- content (TEXT)
- timestamp (TIMESTAMP)

## Frontend Integration

### Docusaurus Plugin
- React component for chatbot interface
- Text selection handler to capture user selections
- API client to communicate with backend

### Features
- Real-time chat interface
- Text selection to ask questions about specific content
- Context-aware responses
- Chat history persistence

## Security Considerations
- API keys stored securely using environment variables
- Rate limiting to prevent abuse
- Input sanitization to prevent injection attacks
- Authentication for personalized features