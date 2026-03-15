"""
RAG（検索拡張生成）システム
ドキュメントをベクトル化してQdrantに保存し、質問時に関連知識を検索
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import json

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import PyPDF2
import markdown
from bs4 import BeautifulSoup

# ==============================
# 設定
# ==============================

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384次元
CHUNK_SIZE = 500  # 文字数
CHUNK_OVERLAP = 50  # オーバーラップ

# ==============================
# RAGシステム
# ==============================

class RAGSystem:
    def __init__(self):
        print("🔧 RAGシステム初期化中...")

        # Qdrantクライアント
        self.client = QdrantClient(url=QDRANT_URL)

        # 埋め込みモデル
        print("📥 埋め込みモデル読み込み中...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ モデル読み込み完了: {EMBEDDING_MODEL}")

        # コレクション初期化
        self._init_collection()

    def _init_collection(self):
        """Qdrantコレクション初期化"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME not in collection_names:
            print(f"📦 コレクション作成中: {COLLECTION_NAME}")
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2の次元数
                    distance=Distance.COSINE
                )
            )
            print(f"✅ コレクション作成完了")
        else:
            print(f"✅ コレクション確認済み: {COLLECTION_NAME}")

    def add_document(self, file_path: str, metadata: Optional[Dict] = None) -> int:
        """ドキュメントを追加"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        print(f"\n📄 ドキュメント処理中: {file_path.name}")

        # ファイル読み込み
        text = self._load_file(file_path)

        if not text.strip():
            print("⚠️ 空のファイルです")
            return 0

        # チャンク分割
        chunks = self._split_text(text)
        print(f"✂️ {len(chunks)} チャンクに分割")

        # メタデータ準備
        if metadata is None:
            metadata = {}

        metadata.update({
            "filename": file_path.name,
            "filepath": str(file_path.absolute()),
            "file_type": file_path.suffix,
            "added_at": datetime.now().isoformat(),
            "total_chunks": len(chunks)
        })

        # ベクトル化と保存
        points = []
        for i, chunk in enumerate(chunks):
            # ベクトル化
            vector = self.embedder.encode(chunk).tolist()

            # ポイント作成
            point_id = self._generate_id(f"{file_path.name}_{i}")

            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_text": chunk,
                "chunk_length": len(chunk)
            })

            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=chunk_metadata
            )

            points.append(point)

        # Qdrantに保存
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        print(f"✅ {len(points)} チャンクを保存しました")
        return len(points)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """知識検索"""
        # クエリをベクトル化
        query_vector = self.embedder.encode(query).tolist()

        # Qdrant検索（新しいAPI）
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True
        ).points

        # 結果整形
        knowledge = []
        for result in results:
            knowledge.append({
                "text": result.payload.get("chunk_text", ""),
                "score": result.score,
                "filename": result.payload.get("filename", "unknown"),
                "chunk_index": result.payload.get("chunk_index", 0),
                "metadata": result.payload
            })

        return knowledge

    def generate_context(self, query: str, top_k: int = 3) -> str:
        """LLMに渡すコンテキスト生成"""
        knowledge = self.search(query, top_k)

        if not knowledge:
            return ""

        context_parts = ["以下の知識を参照してください:\n"]

        for i, item in enumerate(knowledge, 1):
            context_parts.append(f"\n【知識 {i}】（出典: {item['filename']}）")
            context_parts.append(item['text'])
            context_parts.append("")

        return "\n".join(context_parts)

    def delete_document(self, filename: str) -> int:
        """ドキュメント削除"""
        # ファイル名で検索
        results = self.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
                "must": [
                    {
                        "key": "filename",
                        "match": {"value": filename}
                    }
                ]
            },
            limit=10000
        )

        point_ids = [point.id for point in results[0]]

        if point_ids:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=point_ids
            )

        print(f"🗑️ {len(point_ids)} チャンクを削除しました")
        return len(point_ids)

    def list_documents(self) -> List[Dict]:
        """ドキュメント一覧取得"""
        # 全ポイント取得
        results = self.client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000
        )

        # ファイル名ごとに集計
        files = {}
        for point in results[0]:
            filename = point.payload.get("filename", "unknown")
            if filename not in files:
                files[filename] = {
                    "filename": filename,
                    "filepath": point.payload.get("filepath", ""),
                    "file_type": point.payload.get("file_type", ""),
                    "added_at": point.payload.get("added_at", ""),
                    "chunks": 0
                }
            files[filename]["chunks"] += 1

        return list(files.values())

    # ==============================
    # ヘルパー関数
    # ==============================

    def _load_file(self, file_path: Path) -> str:
        """ファイル読み込み"""
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._load_pdf(file_path)
        elif suffix in [".md", ".markdown"]:
            return self._load_markdown(file_path)
        elif suffix == ".txt":
            return self._load_text(file_path)
        elif suffix == ".html":
            return self._load_html(file_path)
        else:
            # その他のテキストファイル
            return self._load_text(file_path)

    def _load_pdf(self, file_path: Path) -> str:
        """PDF読み込み"""
        text_parts = []

        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text())

        return "\n\n".join(text_parts)

    def _load_markdown(self, file_path: Path) -> str:
        """Markdown読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        # HTMLに変換してからテキスト抽出
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()

    def _load_text(self, file_path: Path) -> str:
        """テキストファイル読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_html(self, file_path: Path) -> str:
        """HTML読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()

    def _split_text(self, text: str) -> List[str]:
        """テキストをチャンクに分割"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + CHUNK_SIZE

            # 次のチャンクの開始位置
            next_start = start + CHUNK_SIZE - CHUNK_OVERLAP

            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start = next_start

        return chunks

    def _generate_id(self, text: str) -> int:
        """文字列からIDを生成"""
        hash_value = hashlib.md5(text.encode()).hexdigest()
        return int(hash_value[:8], 16)

# ==============================
# CLI
# ==============================

if __name__ == "__main__":
    import sys

    print("🚀 RAGシステム")
    print("=" * 50)

    rag = RAGSystem()

    if len(sys.argv) < 2:
        print("\n使い方:")
        print("  python rag_system.py add <ファイルパス>     # ドキュメント追加")
        print("  python rag_system.py search <質問>        # 検索")
        print("  python rag_system.py list                 # ドキュメント一覧")
        print("  python rag_system.py delete <ファイル名>  # 削除")
        sys.exit(0)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("エラー: ファイルパスを指定してください")
            sys.exit(1)

        file_path = sys.argv[2]
        rag.add_document(file_path)

    elif command == "search":
        if len(sys.argv) < 3:
            print("エラー: 検索クエリを指定してください")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        print(f"\n🔍 検索: {query}\n")

        knowledge = rag.search(query, top_k=3)

        for i, item in enumerate(knowledge, 1):
            print(f"\n【結果 {i}】スコア: {item['score']:.3f}")
            print(f"出典: {item['filename']} (チャンク {item['chunk_index']})")
            print(f"内容: {item['text'][:200]}...")

    elif command == "list":
        docs = rag.list_documents()

        print(f"\n📚 ドキュメント一覧 ({len(docs)}件)\n")

        for doc in docs:
            print(f"📄 {doc['filename']}")
            print(f"   パス: {doc['filepath']}")
            print(f"   チャンク数: {doc['chunks']}")
            print(f"   追加日時: {doc['added_at']}")
            print()

    elif command == "delete":
        if len(sys.argv) < 3:
            print("エラー: ファイル名を指定してください")
            sys.exit(1)

        filename = sys.argv[2]
        rag.delete_document(filename)

    else:
        print(f"不明なコマンド: {command}")
        sys.exit(1)

    print("\n✅ 完了")
