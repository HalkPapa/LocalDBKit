"""
Text RAG Example
Demonstrates basic RAG operations with text documents
"""
import requests
import json

# Configuration
API_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin"

# Step 1: Login and get token
print("1. Logging in...")
response = requests.post(
    f"{API_URL}/auth/login",
    data={"username": USERNAME, "password": PASSWORD}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Logged in successfully\n")

# Step 2: Add documents
print("2. Adding documents...")
documents = [
    {
        "content": "LocalDBKit is a comprehensive local database environment that includes PostgreSQL with pgvector, MongoDB, Redis, Qdrant vector database, and Ollama for LLM operations.",
        "collection": "demo",
        "metadata": {"type": "introduction"}
    },
    {
        "content": "PostgreSQL with pgvector extension enables vector similarity search, making it perfect for RAG applications and semantic search.",
        "collection": "demo",
        "metadata": {"type": "database", "name": "PostgreSQL"}
    },
    {
        "content": "Qdrant is a high-performance vector database optimized for similarity search and neural network applications.",
        "collection": "demo",
        "metadata": {"type": "database", "name": "Qdrant"}
    }
]

for doc in documents:
    response = requests.post(
        f"{API_URL}/rag/documents",
        headers=headers,
        json=doc
    )
    result = response.json()
    print(f"✓ Added document: {result['id'][:8]}... ({result['preview'][:50]}...)")
print()

# Step 3: Query RAG system
print("3. Querying RAG system...")
queries = [
    "What databases are included in LocalDBKit?",
    "Tell me about vector search capabilities",
    "Which database is best for neural network applications?"
]

for query in queries:
    response = requests.post(
        f"{API_URL}/rag/query",
        headers=headers,
        json={
            "query": query,
            "collection": "demo",
            "use_llm": True,
            "top_k": 3
        }
    )
    result = response.json()

    print(f"\nQ: {query}")
    print(f"A: {result['answer']}")
    print(f"Sources: {len(result['sources'])} documents (scores: {[round(s['score'], 2) for s['score'] in result['sources']]})")

print("\n✓ RAG demo completed!")
