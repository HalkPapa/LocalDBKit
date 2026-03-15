"""
Qdrant の使用例 (Python)
pip install qdrant-client numpy
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, QueryRequest
import numpy as np
from uuid import uuid4

# 接続
client = QdrantClient(host="localhost", port=6333)

print("=== Qdrant 接続テスト ===")
print(f"接続成功: {client.get_collections()}")

# コレクション名
collection_name = "documents"

# 1. コレクション作成
print(f"\n=== コレクション作成: {collection_name} ===")

# 既存のコレクションを削除（テスト用）
try:
    client.delete_collection(collection_name=collection_name)
    print("既存のコレクションを削除しました")
except:
    pass

# 新しいコレクション作成
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
print(f"コレクション '{collection_name}' を作成しました")

# 2. ベクトルとメタデータの追加
print("\n=== ドキュメント追加 ===")

documents = [
    {
        "id": str(uuid4()),
        "text": "Pythonは汎用プログラミング言語です",
        "category": "programming",
        "language": "ja",
        "vector": np.random.rand(384).tolist()
    },
    {
        "id": str(uuid4()),
        "text": "機械学習でモデルを訓練する方法",
        "category": "ai",
        "language": "ja",
        "vector": np.random.rand(384).tolist()
    },
    {
        "id": str(uuid4()),
        "text": "Dockerコンテナの基本的な使い方",
        "category": "devops",
        "language": "ja",
        "vector": np.random.rand(384).tolist()
    },
    {
        "id": str(uuid4()),
        "text": "データベース設計のベストプラクティス",
        "category": "database",
        "language": "ja",
        "vector": np.random.rand(384).tolist()
    },
    {
        "id": str(uuid4()),
        "text": "TypeScriptで型安全なコードを書く",
        "category": "programming",
        "language": "ja",
        "vector": np.random.rand(384).tolist()
    }
]

# ポイントとして追加
points = [
    PointStruct(
        id=doc["id"],
        vector=doc["vector"],
        payload={
            "text": doc["text"],
            "category": doc["category"],
            "language": doc["language"]
        }
    )
    for doc in documents
]

client.upsert(
    collection_name=collection_name,
    points=points
)
print(f"{len(points)}件のドキュメントを追加しました")

# 3. ベクトル検索
print("\n=== ベクトル類似度検索 ===")

# クエリベクトル（実際にはSentence Transformersなどで生成）
query_vector = np.random.rand(384).tolist()

# 類似ドキュメント検索
search_result = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=3
).points

print("類似度の高いドキュメント（上位3件）:")
for i, hit in enumerate(search_result, 1):
    print(f"{i}. {hit.payload['text']}")
    print(f"   カテゴリ: {hit.payload['category']}, スコア: {hit.score:.4f}")

# 4. フィルタ付き検索
print("\n=== フィルタ付き検索 ===")

# 特定のカテゴリのみを検索
filtered_result = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="category",
                match=MatchValue(value="programming")
            )
        ]
    ),
    limit=2
).points

print("プログラミングカテゴリの類似ドキュメント:")
for hit in filtered_result:
    print(f"  - {hit.payload['text']} (スコア: {hit.score:.4f})")

# 5. スクロール（全ドキュメント取得）
print("\n=== 全ドキュメント取得 ===")

scroll_result = client.scroll(
    collection_name=collection_name,
    limit=10
)

points, next_page_offset = scroll_result
print(f"取得したドキュメント数: {len(points)}")
for point in points:
    print(f"  - {point.payload['text'][:30]}... (ID: {point.id})")

# 6. ペイロード更新
print("\n=== ドキュメント更新 ===")

first_doc_id = documents[0]["id"]
client.set_payload(
    collection_name=collection_name,
    payload={
        "category": "programming-language",
        "updated": True
    },
    points=[first_doc_id]
)
print(f"ドキュメント {first_doc_id} を更新しました")

# 7. コレクション情報取得
print("\n=== コレクション情報 ===")
collection_info = client.get_collection(collection_name=collection_name)
print(f"ベクトル数: {collection_info.points_count}")
print(f"ベクトル次元: {collection_info.config.params.vectors.size}")
print(f"距離関数: {collection_info.config.params.vectors.distance}")

# 8. バッチ検索
print("\n=== バッチ検索 ===")

query_vectors = [
    np.random.rand(384).tolist(),
    np.random.rand(384).tolist()
]

batch_results = client.query_batch_points(
    collection_name=collection_name,
    requests=[
        QueryRequest(
            query=query_vectors[0],
            limit=2,
            with_payload=True
        ),
        QueryRequest(
            query=query_vectors[1],
            limit=2,
            with_payload=True
        )
    ]
)

print(f"{len(batch_results)}件のクエリを実行しました")
for i, result in enumerate(batch_results, 1):
    print(f"クエリ{i}の結果:")
    for hit in result.points:
        print(f"  - {hit.payload['text'][:40]}...")

# 9. IDによるドキュメント取得
print("\n=== IDによるドキュメント取得 ===")

# 特定のIDのドキュメントを取得
retrieved = client.retrieve(
    collection_name=collection_name,
    ids=[first_doc_id],
    with_payload=True,
    with_vectors=False
)

print(f"取得したドキュメント:")
for point in retrieved:
    print(f"  ID: {point.id}")
    print(f"  テキスト: {point.payload['text']}")
    print(f"  カテゴリ: {point.payload['category']}")
    if 'updated' in point.payload:
        print(f"  更新済み: {point.payload['updated']}")

# 削除はコメントアウト
# client.delete_collection(collection_name=collection_name)
# print("\nコレクションを削除しました")

print("\n完了!")
print(f"\nダッシュボード: http://localhost:6333/dashboard")
