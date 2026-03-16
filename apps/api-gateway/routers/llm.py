"""
LLM Router
Ollama integration for LLM operations
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Any
from slowapi import Limiter
from slowapi.util import get_remote_address
import httpx
import logging

from routers.auth import get_current_active_user, User
from config import get_settings

router = APIRouter()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


# Models
class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """Chat response model"""
    model: str
    message: ChatMessage
    created_at: str


class EmbeddingRequest(BaseModel):
    """Embedding request model"""
    model: str
    input: str | list[str]


@router.get("/models")
async def list_models(
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    List available LLM models

    Returns list of models from Ollama
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.ollama_url}/api/tags")
            response.raise_for_status()
            data = response.json()

            # Format models for response
            models = []
            for model in data.get("models", []):
                models.append({
                    "name": model.get("name"),
                    "size": model.get("size"),
                    "modified_at": model.get("modified_at"),
                    "digest": model.get("digest", "")[:12]  # Short digest
                })

            return {
                "models": models,
                "count": len(models)
            }
    except httpx.HTTPError as e:
        logger.error(f"Ollama API error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service unavailable: {str(e)}"
        )


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    data: ChatRequest,
    current_user: User = Depends(get_current_active_user)
) -> ChatResponse:
    """
    Chat with LLM

    Supports streaming and non-streaming responses
    Rate limit: 10 requests per minute
    """
    try:
        # Convert messages to Ollama format
        messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]

        # Prepare Ollama request
        ollama_request = {
            "model": data.model,
            "messages": messages,
            "stream": data.stream,
            "options": {
                "temperature": data.temperature
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.ollama_url}/api/chat",
                json=ollama_request
            )
            response.raise_for_status()
            result = response.json()

            return ChatResponse(
                model=result.get("model", data.model),
                message=ChatMessage(
                    role=result.get("message", {}).get("role", "assistant"),
                    content=result.get("message", {}).get("content", "")
                ),
                created_at=result.get("created_at", "")
            )
    except httpx.HTTPError as e:
        logger.error(f"Ollama chat API error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service unavailable: {str(e)}"
        )


@router.post("/embeddings")
async def create_embeddings(
    request: EmbeddingRequest,
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    Generate embeddings for text

    Returns vector embeddings from LLM
    """
    try:
        # Convert input to list if single string
        texts = [request.input] if isinstance(request.input, str) else request.input

        embeddings_list = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                response = await client.post(
                    f"{settings.ollama_url}/api/embeddings",
                    json={
                        "model": request.model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                result = response.json()
                embeddings_list.append(result.get("embedding", []))

        return {
            "model": request.model,
            "embeddings": embeddings_list,
            "count": len(embeddings_list)
        }
    except httpx.HTTPError as e:
        logger.error(f"Ollama embeddings API error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service unavailable: {str(e)}"
        )


class ModelPullRequest(BaseModel):
    """Model pull request"""
    name: str


@router.post("/models/pull")
async def pull_model(
    request: ModelPullRequest,
    current_user: User = Depends(get_current_active_user)
) -> dict[str, Any]:
    """
    Download a model from Ollama

    Args:
        request: Model pull request with model name
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            # Start model pull (non-streaming for simplicity)
            response = await client.post(
                f"{settings.ollama_url}/api/pull",
                json={
                    "name": request.name,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()

            return {
                "model": request.name,
                "status": result.get("status", "success"),
                "message": f"Model {request.name} pull completed"
            }
    except httpx.HTTPError as e:
        logger.error(f"Ollama pull API error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service unavailable: {str(e)}"
        )
