from fastapi import APIRouter, HTTPException, Depends
import openai
from typing import List, Dict, Any
from models import QueryRequest, QueryWithContextRequest, QueryResponse, ChatMessageCreate
from database import get_db_connection
from document_processor import document_processor
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_chat(request: QueryRequest, db=Depends(get_db_connection)):
    """
    Submit a query to the RAG chatbot
    """
    try:
        # Set OpenAI API key and base URL from settings
        openai.api_key = settings.openai_api_key
        openai.api_base = "https://openrouter.ai/api/v1"

        # If no session ID provided, create a new one
        if not request.session_id:
            session_id = await db.create_chat_session()
        else:
            session_id = request.session_id

            # Check if session exists
            session = await db.get_chat_session(session_id)
            if not session:
                session_id = await db.create_chat_session()

        # Search for relevant chunks in vector store
        # Use the vector store from the document processor instance which is properly initialized
        search_results = await document_processor.vector_store.search(request.query, top_k=request.top_k)

        # Collect relevant content and sources
        context_parts = []
        sources = []

        for result in search_results:
            # Support results that may be dicts or objects and may lack payload
            if isinstance(result, dict):
                payload = result.get("payload")
            else:
                payload = getattr(result, "payload", None)

            if not payload:
                # skip results without payload
                continue

            # payload may be a dict with expected fields
            if isinstance(payload, dict):
                content = payload.get("content")
                document_id = payload.get("document_id")
                chunk_index = payload.get("chunk_index")
            else:
                # fallback: try attribute access
                content = getattr(payload, "content", None)
                document_id = getattr(payload, "document_id", None)
                chunk_index = getattr(payload, "chunk_index", None)

            if not content:
                continue

            context_parts.append(content)

            source_info = {
                "id": result.get("id") if isinstance(result, dict) else getattr(result, "id", None),
                "score": result.get("score") if isinstance(result, dict) else getattr(result, "score", None),
                "content": content[:200] + "..." if len(content) > 200 else content,
                "document_id": document_id,
                "chunk_index": chunk_index
            }
            sources.append(source_info)

        # Combine context
        context = "\n\n".join(context_parts)

        # Build the prompt for OpenAI
        if context.strip():
            prompt = f"""
            Answer the question based only on the provided context. If the answer cannot be found in the context, state that you don't have enough information from the provided documents to answer the question.

            Context:
            {context}

            Question: {request.query}

            Answer:
            """
        else:
            prompt = f"""
            I don't have any context from the provided documents to answer your question. The question was: {request.query}
            """

        # Call OpenAI API to generate response (using OpenRouter)
        try:
            response = openai.chat.completions.create(
                model=settings.chat_model if settings.chat_model else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based only on the provided context from the textbook. If the answer is not in the provided context, clearly state that you don't have enough information from the provided documents to answer the question."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            # Extract the response
            answer = response.choices[0].message.content.strip()
        except Exception as llm_error:
            logger.error(f"LLM API error: {llm_error}")
            # Fallback: return document excerpt
            if context.strip():
                answer = f"Based on the provided documents: {context[:300]}..."
            else:
                answer = "I don't have enough information from the provided documents to answer this question."

        # Store the query and response in the database
        await db.add_chat_message(session_id, "user", request.query)
        await db.add_chat_message(session_id, "assistant", answer)

        return QueryResponse(
            response=answer,
            sources=sources,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat query: {str(e)}")

@router.post("/query_with_context", response_model=QueryResponse)
async def query_with_context(request: QueryWithContextRequest, db=Depends(get_db_connection)):
    """
    Submit a query with additional context (selected text) to the RAG chatbot
    """
    try:
        # Set OpenAI API key and base URL from settings
        openai.api_key = settings.openai_api_key
        openai.api_base = "https://openrouter.ai/api/v1"

        # If no session ID provided, create a new one
        if not request.session_id:
            session_id = await db.create_chat_session()
        else:
            session_id = request.session_id

            # Check if session exists
            session = await db.get_chat_session(session_id)
            if not session:
                session_id = await db.create_chat_session()

        # Search for relevant chunks in vector store
        search_results = await document_processor.vector_store.search(request.query, top_k=request.top_k)

        # Collect relevant content and sources
        context_parts = [request.context]  # Start with the user-provided context
        sources = []

        # Add retrieved context from vector store
        for result in search_results:
            # Support results that may be dicts or objects and may lack payload
            if isinstance(result, dict):
                payload = result.get("payload")
            else:
                payload = getattr(result, "payload", None)

            if not payload:
                continue

            if isinstance(payload, dict):
                content = payload.get("content")
                document_id = payload.get("document_id")
                chunk_index = payload.get("chunk_index")
            else:
                content = getattr(payload, "content", None)
                document_id = getattr(payload, "document_id", None)
                chunk_index = getattr(payload, "chunk_index", None)

            if not content:
                continue

            context_parts.append(content)

            source_info = {
                "id": result.get("id") if isinstance(result, dict) else getattr(result, "id", None),
                "score": result.get("score") if isinstance(result, dict) else getattr(result, "score", None),
                "content": content[:200] + "..." if len(content) > 200 else content,
                "document_id": document_id,
                "chunk_index": chunk_index
            }
            sources.append(source_info)

        # Combine all context
        combined_context = "\n\n".join(context_parts)

        # Build the prompt for OpenAI
        prompt = f"""
        Answer the question based on the provided context and selected text. The user has selected the following text:

        Selected Text:
        {request.context}

        Additional Context:
        {combined_context}

        Question: {request.query}

        Answer:
        """

        # Call OpenAI API to generate response
        try:
            response = openai.chat.completions.create(
                model=settings.chat_model if settings.chat_model else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context and selected text from the textbook. Focus on addressing the question in relation to the selected text and the context provided."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            # Extract the response
            answer = response.choices[0].message.content.strip()
        except Exception as llm_error:
            logger.error(f"LLM API error: {llm_error}")
            # Fallback: return document excerpt
            if combined_context.strip():
                answer = f"Based on the provided documents and selected text: {combined_context[:300]}..."
            else:
                answer = "I don't have enough information from the provided documents to answer this question."

        # Store the query and response in the database
        await db.add_chat_message(session_id, "user", f"Context: {request.context}\nQuestion: {request.query}")
        await db.add_chat_message(session_id, "assistant", answer)

        return QueryResponse(
            response=answer,
            sources=sources,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error processing chat query with context: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat query with context: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db=Depends(get_db_connection)):
    """
    Retrieve chat history for a session
    """
    try:
        messages = await db.get_chat_messages(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")