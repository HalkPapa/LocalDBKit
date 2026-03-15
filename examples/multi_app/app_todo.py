#!/usr/bin/env python3
"""
Todoアプリのサンプルコード
作成者: Claude Sonnet 4.5 (Anthropic)
作成日: 2026年3月9日

このサンプルは、Todoアプリのデータを複数のデータベースで管理する例です。
- PostgreSQL: ユーザー管理
- MongoDB: Todoアイテム、プロジェクト
- Redis: キャッシュ、セッション
- Qdrant: セマンティック検索（類似Todoの検索）
"""

import psycopg2
from pymongo import MongoClient
import redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import random
from datetime import datetime, timedelta

# 設定
APP_NAME = "app_todo"
POSTGRES_URL = f"postgresql://postgres:postgres@localhost:5432/{APP_NAME}"
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
QDRANT_URL = "http://localhost:6333"
REDIS_PREFIX = f"{APP_NAME}:"
QDRANT_COLLECTION = f"{APP_NAME}_vectors"


def redis_key(key):
    return f"{REDIS_PREFIX}{key}"


def setup_databases():
    """データベースセットアップ"""
    print("\n=== データベースセットアップ ===")

    # PostgreSQL: ユーザーテーブル
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✓ PostgreSQLテーブル作成完了")

    # MongoDB: Todoコレクション
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]
    db.create_collection("todos", capped=False)
    db.create_collection("projects", capped=False)
    mongo_client.close()
    print("✓ MongoDBコレクション作成完了")

    # Qdrant: Todoベクトルコレクション
    qdrant = QdrantClient(url=QDRANT_URL)
    try:
        qdrant.get_collection(QDRANT_COLLECTION)
        print(f"⚠ Qdrantコレクション '{QDRANT_COLLECTION}' は既に存在します")
    except:
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=128, distance=Distance.COSINE)
        )
        print("✓ Qdrantコレクション作成完了")


def create_user(email, name):
    """ユーザー作成"""
    print(f"\n=== ユーザー作成: {name} ({email}) ===")

    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (email, name)
            VALUES (%s, %s)
            RETURNING id
        """, (email, name))
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"✓ ユーザーID: {user_id}")
    except psycopg2.IntegrityError:
        conn.rollback()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_id = cur.fetchone()[0]
        print(f"⚠ ユーザーは既に存在します (ID: {user_id})")

    cur.close()
    conn.close()

    # Redisにキャッシュ
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.hset(redis_key(f"user:{user_id}"), mapping={
        "email": email,
        "name": name
    })
    r.expire(redis_key(f"user:{user_id}"), 3600)  # 1時間

    return user_id


def create_todo(user_id, title, description, priority="medium"):
    """Todo作成"""
    print(f"\n=== Todo作成: {title} ===")

    # MongoDB: Todoドキュメント
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]

    todo = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now(),
        "due_date": datetime.now() + timedelta(days=7)
    }

    result = db.todos.insert_one(todo)
    todo_id = str(result.inserted_id)
    print(f"✓ TodoID: {todo_id}")

    mongo_client.close()

    # Qdrant: セマンティック検索用ベクトル
    # 実際は埋め込みモデルで生成、ここではダミー
    vector = [random.random() for _ in range(128)]

    qdrant = QdrantClient(url=QDRANT_URL)
    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=hash(todo_id) % (10**10),  # 整数IDに変換
                vector=vector,
                payload={
                    "todo_id": todo_id,
                    "title": title,
                    "description": description,
                    "priority": priority
                }
            )
        ]
    )
    print("✓ ベクトル追加（セマンティック検索可能）")

    # Redis: 統計情報更新
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.hincrby(redis_key(f"stats:user:{user_id}"), "total_todos", 1)
    r.hincrby(redis_key(f"stats:user:{user_id}"), "pending_todos", 1)

    return todo_id


def complete_todo(todo_id, user_id):
    """Todo完了"""
    print(f"\n=== Todo完了: {todo_id} ===")

    # MongoDB: ステータス更新
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]

    from bson.objectid import ObjectId
    result = db.todos.update_one(
        {"_id": ObjectId(todo_id)},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now()
            }
        }
    )

    if result.modified_count > 0:
        print("✓ Todo完了")
    else:
        print("⚠ Todoが見つかりません")

    mongo_client.close()

    # Redis: 統計情報更新
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.hincrby(redis_key(f"stats:user:{user_id}"), "pending_todos", -1)
    r.hincrby(redis_key(f"stats:user:{user_id}"), "completed_todos", 1)


def search_similar_todos(query_text):
    """類似Todo検索"""
    print(f"\n=== 類似Todo検索: '{query_text}' ===")

    # ダミークエリベクトル（実際は埋め込みモデルで生成）
    query_vector = [random.random() for _ in range(128)]

    qdrant = QdrantClient(url=QDRANT_URL)

    try:
        results = qdrant.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vector,
            limit=3
        ).points

        print("\n類似Todo:")
        for result in results:
            print(f"  - {result.payload['title']} ({result.payload['priority']})")
            print(f"    {result.payload['description']}")
            print(f"    類似度スコア: {result.score:.4f}")
    except Exception as e:
        print(f"✗ 検索エラー: {e}")


def display_user_dashboard(user_id):
    """ユーザーダッシュボード表示"""
    print(f"\n=== ダッシュボード (User ID: {user_id}) ===")

    # PostgreSQL: ユーザー情報
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()
    cur.execute("SELECT email, name FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    if user:
        print(f"\nユーザー: {user[1]} ({user[0]})")

    cur.close()
    conn.close()

    # MongoDB: Todo一覧
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]

    pending_todos = list(db.todos.find({"user_id": user_id, "status": "pending"}))
    completed_todos = list(db.todos.find({"user_id": user_id, "status": "completed"}))

    print(f"\n未完了Todo: {len(pending_todos)}件")
    for todo in pending_todos[:5]:  # 最新5件
        print(f"  - [{todo['priority']}] {todo['title']}")

    print(f"\n完了Todo: {len(completed_todos)}件")

    mongo_client.close()

    # Redis: 統計情報
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    stats = r.hgetall(redis_key(f"stats:user:{user_id}"))

    if stats:
        print("\n統計:")
        print(f"  総Todo数: {stats.get('total_todos', 0)}")
        print(f"  未完了: {stats.get('pending_todos', 0)}")
        print(f"  完了済み: {stats.get('completed_todos', 0)}")


def main():
    """メイン処理"""
    print("=" * 50)
    print("  Todoアプリ - データベース管理例")
    print("=" * 50)

    # セットアップ
    setup_databases()

    # ユーザー作成
    user_id = create_user("alice@example.com", "Alice")

    # Todo作成
    todo1 = create_todo(user_id, "Buy groceries", "Milk, eggs, bread", "high")
    todo2 = create_todo(user_id, "Write report", "Q1 financial report", "medium")
    todo3 = create_todo(user_id, "Call dentist", "Schedule appointment", "low")
    todo4 = create_todo(user_id, "Code review", "Review PR #123", "high")

    # Todo完了
    complete_todo(todo1, user_id)

    # 類似Todo検索
    search_similar_todos("Write documentation")

    # ダッシュボード表示
    display_user_dashboard(user_id)

    print("\n" + "=" * 50)
    print("  完了！")
    print("=" * 50)


if __name__ == "__main__":
    main()
