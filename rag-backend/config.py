import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Force load .env from this folder
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Qdrant settings
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")
    
    # Neon DB
    neon_database_url: str = os.getenv("NEON_DATABASE_URL", "")
    
    # App settings
    app_name: str = "RAG Chatbot API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4.1-mini")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
