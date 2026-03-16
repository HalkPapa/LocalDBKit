# Multimodal RAG Examples

Examples demonstrating Retrieval-Augmented Generation (RAG) with multimodal support.

## 📋 Prerequisites

- LocalDBKit services running (`make up` or `docker compose up -d`)
- Python 3.11+
- Required packages: `requests`, `pillow`

## 🚀 Quick Start

### Install Dependencies

```bash
pip install requests pillow
```

### Run Examples

#### 1. Text RAG Example

```bash
python text_rag_example.py
```

Demonstrates:
- Adding text documents to RAG
- Semantic search with embeddings
- LLM-powered question answering

#### 2. Multimodal RAG Example

```bash
python multimodal_rag_example.py
```

Demonstrates:
- Adding text, images, and PDFs
- OCR text extraction from images
- Cross-modal semantic search
- Unified query across all modalities

## 📊 Architecture

```
User Query
    ↓
[Embedding Generation (Ollama)]
    ↓
[Vector Search (Qdrant)]
    ↓
[Retrieved Documents]
    ├── Text Documents
    ├── Image (via OCR)
    └── PDF (via PyMuPDF)
    ↓
[LLM Answer Generation (Ollama)]
    ↓
Final Answer
```

## 🔑 API Endpoints Used

### Authentication
- `POST /api/v1/auth/login` - Get JWT token

### Document Management
- `POST /api/v1/rag/documents` - Add text document
- `POST /api/v1/rag/documents/image` - Add image document
- `POST /api/v1/rag/documents/pdf` - Add PDF document
- `GET /api/v1/rag/documents` - List documents
- `DELETE /api/v1/rag/documents/{id}` - Delete document

### Querying
- `POST /api/v1/rag/query` - Query RAG system

### Collections
- `GET /api/v1/rag/collections` - List collections

## 💡 Usage Examples

### Adding a Text Document

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "admin", "password": "admin"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Add document
response = requests.post(
    "http://localhost:8000/api/v1/rag/documents",
    headers=headers,
    json={
        "content": "Your document text here",
        "collection": "my_collection",
        "metadata": {"source": "example"}
    }
)
print(response.json())
```

### Adding an Image Document

```python
# Upload image
with open("image.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/rag/documents/image",
        headers=headers,
        files={"file": f},
        data={"collection": "my_collection"}
    )
print(response.json())
```

### Querying RAG

```python
# Query
response = requests.post(
    "http://localhost:8000/api/v1/rag/query",
    headers=headers,
    json={
        "query": "What is LocalDBKit?",
        "collection": "my_collection",
        "use_llm": True,
        "top_k": 3
    }
)
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])} documents")
```

## 🧪 Testing

Run the examples to test your setup:

```bash
# Test text RAG
python text_rag_example.py

# Test multimodal RAG
python multimodal_rag_example.py
```

## 📝 Notes

- Default collection: `knowledge_base`
- Embedding model: `gemma2:9b` (3584 dimensions)
- Vector distance: Cosine similarity
- Default top_k: 5 documents
- LLM model: `gemma2:9b`

## 🔧 Configuration

Edit the scripts to customize:
- API URL
- Collection names
- Model selection
- Search parameters

## 📖 Learn More

- [API Gateway Guide](../../docs/guides/API_GATEWAY_GUIDE.md)
- [RAG Documentation](../../docs/guides/RAG_GUIDE.md)
- [Multimodal Processing](../../apps/multimodal-processor/README.md)

---

**Created**: 2026-03-16
**Version**: 0.3.0
