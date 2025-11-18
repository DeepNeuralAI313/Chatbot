"""
RAG (Retrieval-Augmented Generation) Service

This service handles:
- Text chunking and processing
- Embedding generation and storage
- Semantic search using ChromaDB

Embeddings are stored persistently in: backend/data/embeddings_db/
This allows embeddings to be reused across server restarts without regenerating them.
"""

import os
import chromadb
from pathlib import Path
from typing import List, Tuple
from .embedding_service import get_embedding

# Set up persistent storage directory
STORAGE_DIR = Path(__file__).parent.parent / "data" / "embeddings_db"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize ChromaDB client with persistent storage
chroma_client = chromadb.PersistentClient(path=str(STORAGE_DIR))

# Global collection variable
collection = None

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 75) -> List[str]:
    """
    Split text into chunks with overlap
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence or word boundary
        if end < text_length:
            # Look for sentence end
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # At least 50% through the chunk
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks

def initialize_rag():
    """Initialize the RAG system by loading and processing the article"""
    global collection
    
    # Load article
    article_path = Path(__file__).parent.parent / "data" / "article.txt"
    
    if not article_path.exists():
        raise FileNotFoundError(f"Article not found at {article_path}")
    
    with open(article_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    
    # Chunk the text
    chunks = chunk_text(article_text)
    print(f"Created {len(chunks)} chunks from article")
    
    # Create or get collection (will load from persistent storage if exists)
    try:
        collection = chroma_client.get_collection(name="iptv_knowledge")
        print(f"✅ Loaded existing embeddings from persistent storage: {STORAGE_DIR}")
        print(f"   Collection contains {collection.count()} embeddings")
    except:
        collection = chroma_client.create_collection(name="iptv_knowledge")
        
        # Generate embeddings and add to collection
        print("🔄 Generating embeddings for chunks...")
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            if embedding:
                collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    ids=[f"chunk_{i}"]
                )
            
            # Progress indicator
            if (i + 1) % 5 == 0:
                print(f"   Processed {i + 1}/{len(chunks)} chunks...")
        
        print(f"✅ Saved {len(chunks)} embeddings to persistent storage: {STORAGE_DIR}")
    
    return collection

def search_knowledge(query: str, top_k: int = 3) -> Tuple[List[str], float]:
    """
    Search for relevant chunks given a query
    
    Args:
        query: User's question
        top_k: Number of top results to return
    
    Returns:
        Tuple of (list of relevant chunks, average similarity score)
    """
    global collection
    
    if collection is None:
        initialize_rag()
    
    # Generate embedding for query
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        return [], 0.0
    
    # Search in collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # Extract documents and calculate average distance
    documents = results['documents'][0] if results['documents'] else []
    distances = results['distances'][0] if results['distances'] else []
    
    # Convert distance to similarity (ChromaDB uses cosine distance)
    # Similarity = 1 - distance (for normalized vectors)
    similarities = [1 - d for d in distances] if distances else []
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    
    return documents, avg_similarity

def get_conversation_context(conversation_history: List[dict], max_messages: int = 5) -> str:
    """
    Build context from recent conversation history for memory
    
    Args:
        conversation_history: List of message dicts with role and content
        max_messages: Maximum number of messages to include
    
    Returns:
        Formatted conversation context string
    """
    if not conversation_history:
        return ""
    
    # Get last N messages
    recent_messages = conversation_history[-max_messages:]
    
    # Format as conversation
    context_lines = []
    for msg in recent_messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        context_lines.append(f"{role}: {msg['content']}")
    
    return "\n".join(context_lines)
