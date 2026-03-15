"""
PostgreSQL + pgvector の使用例 (Python)
pip install psycopg2-binary numpy
"""

import psycopg2
from psycopg2.extras import execute_values, Json
import numpy as np

# 接続
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

# 1. 基本的なCRUD操作
print("=== 基本的なCRUD操作 ===")

# ユーザーを追加
cur.execute("""
    INSERT INTO users (username, email)
    VALUES (%s, %s)
    ON CONFLICT (username) DO NOTHING
    RETURNING id, username
""", ("charlie", "charlie@example.com"))

if cur.rowcount > 0:
    user_id, username = cur.fetchone()
    print(f"ユーザー作成: {username} (ID: {user_id})")

# ユーザー一覧を取得
cur.execute("SELECT * FROM users")
users = cur.fetchall()
print(f"ユーザー数: {len(users)}")
for user in users:
    print(f"  - {user[1]} ({user[2]})")

# 2. ベクトル検索の例
print("\n=== ベクトル検索 ===")

# サンプルドキュメントを追加（ダミーのベクトル）
documents = [
    ("Python入門", "Pythonプログラミングの基礎を学ぶ", np.random.rand(1536).tolist()),
    ("機械学習入門", "機械学習の基本概念とアルゴリズム", np.random.rand(1536).tolist()),
    ("データベース設計", "効率的なデータベース設計の方法", np.random.rand(1536).tolist()),
]

for title, content, embedding in documents:
    cur.execute("""
        INSERT INTO documents (title, content, embedding, metadata)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (title, content, embedding, Json({"category": "tutorial"})))

conn.commit()

# クエリベクトルを生成（実際にはOpenAI APIなどで生成）
query_embedding = np.random.rand(1536).tolist()

# ベクトル類似度検索（コサイン類似度）
cur.execute("""
    SELECT id, title, content,
           1 - (embedding <=> %s::vector) as similarity
    FROM documents
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> %s::vector
    LIMIT 3
""", (query_embedding, query_embedding))

results = cur.fetchall()
print("類似ドキュメント:")
for doc_id, title, content, similarity in results:
    print(f"  - {title} (類似度: {similarity:.4f})")

# クリーンアップ
cur.close()
conn.close()

print("\n接続を閉じました")
