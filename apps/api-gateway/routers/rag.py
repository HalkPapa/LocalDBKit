"""
RAG Router
Retrieval-Augmented Generation with multimodal support
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Any, Optional, List
import httpx
import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from routers.auth import get_current_active_user, User
from config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


# Models
class RAGQueryRequest(BaseModel):
    """RAG query request model"""
    query: str
    top_k: int = 5
    collection: str = "knowledge_base"
    use_llm: bool = True


class RAGQueryResponse(BaseModel):
    """RAG query response model"""
    query: str
    answer: str
    sources: list[dict[str, Any]]


class DocumentRequest(BaseModel):
    """Document request model"""
    content: str
    metadata: dict[str, Any] = {}
    collection: str = "knowledge_base"


# Initialize Qdrant client
qdrant_client = QdrantClient(url=settings.qdrant_url)


async def get_embeddings(text: str, model: str = "gemma2:9b") -> List[float]:
    """Generate embeddings using Ollama"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ollama_url}/api/embeddings",
                json={"model": model, "prompt": text}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def ensure_collection(collection_name: str, vector_size: int = 3584):
    """Ensure collection exists in Qdrant"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection_name not in collection_names:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {collection_name}")
    except Exception as e:
        logger.error(f"Collection creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform RAG query

    Retrieves relevant documents and generates answer
    """
    try:
        # Generate query embeddings
        query_embeddings = await get_embeddings(request.query)

        # Search in Qdrant
        search_result = qdrant_client.search(
            collection_name=request.collection,
            query_vector=query_embeddings,
            limit=request.top_k
        )

        # Extract documents
        sources = []
        for hit in search_result:
            sources.append({
                "id": str(hit.id),
                "text": hit.payload.get("text", hit.payload.get("content", "")),
                "score": hit.score,
                "metadata": hit.payload.get("metadata", {}),
                "source": hit.payload.get("source", "text")
            })

        # Generate LLM response if requested
        answer = ""
        if request.use_llm and sources:
            context = "\n\n".join([doc["text"] for doc in sources[:3]])
            prompt = f"Context:\n{context}\n\nQuestion: {request.query}\n\nAnswer based on the context above:"

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.ollama_url}/api/chat",
                    json={
                        "model": "gemma2:9b",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                answer = result.get("message", {}).get("content", "")
        else:
            answer = "Set use_llm=true to generate AI answer"

        return RAGQueryResponse(
            query=request.query,
            answer=answer,
            sources=sources
        )

    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents")
async def add_document(
    request: DocumentRequest,
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    Add document to RAG system

    Processes and stores document in vector database
    """
    try:
        # Generate embeddings
        embeddings = await get_embeddings(request.content)

        # Ensure collection exists
        await ensure_collection(request.collection, len(embeddings))

        # Generate document ID
        doc_id = str(uuid.uuid4())

        # Store in Qdrant
        qdrant_client.upsert(
            collection_name=request.collection,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=embeddings,
                    payload={
                        "text": request.content,
                        "content": request.content,
                        "metadata": request.metadata,
                        "source": "text"
                    }
                )
            ]
        )

        return {
            "id": doc_id,
            "collection": request.collection,
            "status": "added",
            "preview": request.content[:100] + "..." if len(request.content) > 100 else request.content
        }

    except Exception as e:
        logger.error(f"Document add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/image")
async def add_image_document(
    file: UploadFile = File(...),
    collection: str = Form("knowledge_base"),
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    Add image document to RAG system

    Extracts text via OCR and stores in vector database
    """
    try:
        # Extract text from image
        content = await file.read()

        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (file.filename, content, file.content_type)}
            response = await client.post(
                "http://multimodal-processor:8001/api/v1/ocr/extract",
                files=files
            )
            response.raise_for_status()
            ocr_result = response.json()

        extracted_text = ocr_result.get("text", "")
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text found in image")

        # Generate embeddings and store
        embeddings = await get_embeddings(extracted_text)
        await ensure_collection(collection, len(embeddings))

        doc_id = str(uuid.uuid4())
        qdrant_client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=embeddings,
                    payload={
                        "text": extracted_text,
                        "source": "image",
                        "filename": file.filename,
                        "ocr_confidence": ocr_result.get("confidence", 0),
                        "metadata": {
                            "word_count": ocr_result.get("word_count", 0),
                            "image_size": ocr_result.get("image_size", {})
                        }
                    }
                )
            ]
        )

        return {
            "id": doc_id,
            "collection": collection,
            "source": "image",
            "filename": file.filename,
            "extracted_text": extracted_text[:100] + "...",
            "ocr_confidence": ocr_result.get("confidence", 0)
        }

    except Exception as e:
        logger.error(f"Image document add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/pdf")
async def add_pdf_document(
    file: UploadFile = File(...),
    collection: str = Form("knowledge_base"),
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    Add PDF document to RAG system

    Extracts text from PDF and stores in vector database
    """
    try:
        # Extract text from PDF
        content = await file.read()

        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"file": (file.filename, content, "application/pdf")}
            response = await client.post(
                "http://multimodal-processor:8001/api/v1/pdf/extract",
                files=files
            )
            response.raise_for_status()
            pdf_result = response.json()

        extracted_text = pdf_result.get("full_text", "")
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text found in PDF")

        # Generate embeddings and store
        embeddings = await get_embeddings(extracted_text)
        await ensure_collection(collection, len(embeddings))

        doc_id = str(uuid.uuid4())
        qdrant_client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=embeddings,
                    payload={
                        "text": extracted_text,
                        "source": "pdf",
                        "filename": file.filename,
                        "metadata": {
                            "page_count": pdf_result.get("page_count", 0),
                            "total_word_count": pdf_result.get("total_word_count", 0)
                        }
                    }
                )
            ]
        )

        return {
            "id": doc_id,
            "collection": collection,
            "source": "pdf",
            "filename": file.filename,
            "page_count": pdf_result.get("page_count", 0),
            "word_count": pdf_result.get("total_word_count", 0)
        }

    except Exception as e:
        logger.error(f"PDF document add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(
    collection: str = "knowledge_base",
    limit: int = 10,
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """List documents in collection"""
    try:
        result = qdrant_client.scroll(
            collection_name=collection,
            limit=limit
        )

        documents = []
        for point in result[0]:
            documents.append({
                "id": str(point.id),
                "text": point.payload.get("text", point.payload.get("content", ""))[:100] + "...",
                "source": point.payload.get("source", "text"),
                "metadata": point.payload.get("metadata", {})
            })

        return {
            "collection": collection,
            "documents": documents,
            "count": len(documents)
        }

    except Exception as e:
        logger.error(f"Document listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    collection: str = "knowledge_base",
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """Delete document from RAG system"""
    try:
        qdrant_client.delete(
            collection_name=collection,
            points_selector=[document_id]
        )

        return {
            "id": document_id,
            "collection": collection,
            "status": "deleted"
        }

    except Exception as e:
        logger.error(f"Document deletion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def list_collections(
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """List available RAG collections"""
    try:
        collections = qdrant_client.get_collections().collections
        collection_list = []
        for c in collections:
            # Get collection info for detailed stats
            try:
                info = qdrant_client.get_collection(c.name)
                collection_list.append({
                    "name": c.name,
                    "vectors_count": info.vectors_count if hasattr(info, 'vectors_count') else 0,
                    "points_count": info.points_count if hasattr(info, 'points_count') else 0,
                })
            except:
                # Fallback if detailed info fails
                collection_list.append({"name": c.name})

        return {
            "collections": collection_list,
            "count": len(collection_list)
        }
    except Exception as e:
        logger.error(f"Collection listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
