"""
Multimodal RAG Example
Demonstrates RAG operations with text, images, and PDFs
"""
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration
API_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin"
COLLECTION = "multimodal_demo"

# Step 1: Login
print("1. Logging in...")
response = requests.post(
    f"{API_URL}/auth/login",
    data={"username": USERNAME, "password": PASSWORD}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Logged in successfully\n")

# Step 2: Add text document
print("2. Adding text document...")
response = requests.post(
    f"{API_URL}/rag/documents",
    headers=headers,
    json={
        "content": "LocalDBKit provides a complete local development environment with PostgreSQL, MongoDB, Redis, Qdrant, and Ollama.",
        "collection": COLLECTION,
        "metadata": {"type": "text", "topic": "overview"}
    }
)
print(f"✓ Text document added: {response.json()['id'][:8]}...\n")

# Step 3: Create and add image document
print("3. Creating test image with text...")
img = Image.new('RGB', (600, 150), color='white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 36)
except:
    font = ImageFont.load_default()

draw.text((20, 50), 'Vector Database Architecture', fill='black', font=font)

# Save to bytes
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

print("4. Adding image document to RAG...")
response = requests.post(
    f"{API_URL}/rag/documents/image",
    headers=headers,
    files={"file": ("diagram.png", img_bytes, "image/png")},
    data={"collection": COLLECTION}
)
result = response.json()
print(f"✓ Image added: {result['id'][:8]}...")
print(f"  Extracted text: \"{result['extracted_text']}\"")
print(f"  OCR confidence: {result['ocr_confidence']}%\n")

# Step 4: Query multimodal RAG
print("5. Querying multimodal RAG system...")
queries = [
    "What is mentioned in the image?",
    "What services does LocalDBKit provide?",
    "Tell me about the vector database"
]

for query in queries:
    response = requests.post(
        f"{API_URL}/rag/query",
        headers=headers,
        json={
            "query": query,
            "collection": COLLECTION,
            "use_llm": True,
            "top_k": 5
        }
    )
    result = response.json()

    print(f"\nQ: {query}")
    print(f"A: {result['answer']}")

    # Show sources with their types
    sources_info = []
    for src in result['sources']:
        source_type = src['source']
        score = round(src['score'], 2)
        sources_info.append(f"{source_type}({score})")

    print(f"Sources: {', '.join(sources_info)}")

print("\n✓ Multimodal RAG demo completed!")
print("\n📊 Summary:")
print("- Added text documents")
print("- Generated and processed image with OCR")
print("- Queried across multiple modalities")
print("- LLM synthesized answers from diverse sources")
