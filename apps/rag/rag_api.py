"""
RAG API Server
FastAPIでRAG検索エンドポイントを提供
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from rag_system import RAGSystem

# FastAPIアプリ
app = FastAPI(
    title="RAG Knowledge API",
    description="RAG検索APIサーバー",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAGシステム初期化
rag = RAGSystem()

# ==============================
# データモデル
# ==============================

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class SearchResult(BaseModel):
    text: str
    score: float
    filename: str
    chunk_index: int
    metadata: dict

class AddDocumentRequest(BaseModel):
    file_path: str
    metadata: Optional[dict] = None

class DeleteDocumentRequest(BaseModel):
    filename: str

# ==============================
# エンドポイント
# ==============================

@app.get("/")
async def root():
    """API情報"""
    return {
        "name": "RAG Knowledge API",
        "version": "1.0.0",
        "endpoints": {
            "/search": "POST - 知識検索",
            "/documents": "GET - ドキュメント一覧",
            "/documents/add": "POST - ドキュメント追加",
            "/documents/delete": "DELETE - ドキュメント削除",
            "/health": "GET - ヘルスチェック"
        }
    }

@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "healthy"}

@app.post("/search", response_model=List[SearchResult])
async def search_knowledge(request: SearchRequest):
    """
    知識検索

    質問文をベクトル化し、類似度の高いチャンクを検索します。
    """
    try:
        results = rag.search(request.query, top_k=request.top_k)

        return [
            SearchResult(
                text=r["text"],
                score=r["score"],
                filename=r["filename"],
                chunk_index=r["chunk_index"],
                metadata=r["metadata"]
            )
            for r in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """ドキュメント一覧取得"""
    try:
        docs = rag.list_documents()
        return docs

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/add")
async def add_document(request: AddDocumentRequest):
    """ドキュメント追加"""
    try:
        chunks_added = rag.add_document(
            request.file_path,
            metadata=request.metadata
        )

        return {
            "status": "success",
            "file_path": request.file_path,
            "chunks_added": chunks_added
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/delete")
async def delete_document(request: DeleteDocumentRequest):
    """ドキュメント削除"""
    try:
        chunks_deleted = rag.delete_document(request.filename)

        return {
            "status": "success",
            "filename": request.filename,
            "chunks_deleted": chunks_deleted
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/context")
async def generate_context(request: SearchRequest):
    """
    LLM用コンテキスト生成

    検索結果を整形してLLMに渡しやすい形式で返します。
    """
    try:
        context = rag.generate_context(request.query, top_k=request.top_k)

        return {
            "context": context,
            "query": request.query
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# メイン
# ==============================

if __name__ == "__main__":
    print("🚀 RAG API Server")
    print("=" * 50)
    print("📡 URL: http://localhost:8003")
    print("📖 Docs: http://localhost:8003/docs")
    print("=" * 50)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
