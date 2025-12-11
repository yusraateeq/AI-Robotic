"""
Utility script to load textbook content into the RAG system
"""
import asyncio
import os
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from the rag-backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from document_processor import document_processor

async def load_textbook_chapters():
    """
    Load all textbook chapters from the my-website/docs directory into the RAG system
    """
    # Initialize DB and vector store
    print("✅ Initializing database and vector store...")
    await document_processor.db.connect()
    await document_processor.vector_store.init()
    
    # Path to the textbook content
    docs_dir = Path("../my-website/docs")
    
    # Define the order of chapters to process
    chapter_files = [
        "intro.md",
        "chapter_01_physical_ai.md",
        "chapter_02_humanoid_robotics.md",
        "chapter_03_ros2_fundamentals.md",
        "chapter_04_Digital_Twin_Simulation.md",
        "chapter_05_vla_systems.md",
        "chapter_06_capstone.md"
    ]
    
    for chapter_file in chapter_files:
        file_path = docs_dir / chapter_file
        
        if file_path.exists():
            print(f"\nProcessing {chapter_file}...")
            
            # Read the content of the chapter
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from the first line or filename
            title = chapter_file.replace('.md', '').replace('_', ' ').title()
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()  # Remove '# ' prefix
                    break
            
            print(f"Title: {title}")
            
            # Process and store the document
            try:
                document_id = await document_processor.process_and_store_document(
                    title=title,
                    content=content,
                    source_path=str(file_path),
                    metadata={
                        "source": "textbook",
                        "chapter_file": chapter_file,
                        "type": "textbook_chapter"
                    }
                )
                print(f"✓ Successfully indexed {chapter_file} with ID: {document_id}")
            except Exception as e:
                print(f"✗ Error indexing {chapter_file}: {str(e)}")
        else:
            print(f"File not found: {chapter_file}")
    
    print("\nTextbook loading completed!")

if __name__ == "__main__":
    if not settings.openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    if not settings.neon_database_url:
        print("Error: NEON_DATABASE_URL environment variable not set")
        exit(1)
    
    if not settings.qdrant_url:
        print("Error: QDRANT_URL environment variable not set")
        exit(1)
    
    # Run the async function
    asyncio.run(load_textbook_chapters())
