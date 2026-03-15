#!/usr/bin/env python3
"""
RPGゲームのサンプルコード
作成者: Claude Sonnet 4.5 (Anthropic)
作成日: 2026年3月9日

このサンプルは、RPGゲームのデータを4つのデータベースで管理する例です。
- PostgreSQL: プレイヤー、インベントリ
- MongoDB: クエスト、実績
- Redis: セッション、リアルタイムステータス
- Qdrant: アイテム類似検索
"""

import psycopg2
from pymongo import MongoClient
import redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import random

# 設定
APP_NAME = "game_rpg"
POSTGRES_URL = f"postgresql://postgres:postgres@localhost:5432/{APP_NAME}"
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
QDRANT_URL = "http://localhost:6333"
REDIS_PREFIX = f"{APP_NAME}:"
QDRANT_COLLECTION = f"{APP_NAME}_items"


def redis_key(key):
    return f"{REDIS_PREFIX}{key}"


def setup_databases():
    """データベースセットアップ"""
    print("\n=== データベースセットアップ ===")

    # PostgreSQL: プレイヤーテーブル
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            level INTEGER DEFAULT 1,
            hp INTEGER DEFAULT 100,
            mp INTEGER DEFAULT 50,
            gold INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            item_name VARCHAR(100),
            quantity INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✓ PostgreSQLテーブル作成完了")

    # MongoDB: クエストコレクション
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]
    db.create_collection("quests", capped=False)
    db.create_collection("achievements", capped=False)
    mongo_client.close()
    print("✓ MongoDBコレクション作成完了")

    # Qdrant: アイテムコレクション
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


def create_player(name, player_class="Warrior"):
    """プレイヤー作成"""
    print(f"\n=== プレイヤー作成: {name} ({player_class}) ===")

    # PostgreSQL: プレイヤーデータ
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO players (name, level, hp, mp, gold)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (name, 1, 100, 50, 100))
    player_id = cur.fetchone()[0]
    conn.commit()

    # 初期装備
    cur.execute("""
        INSERT INTO inventory (player_id, item_name, quantity)
        VALUES (%s, %s, %s)
    """, (player_id, "Wooden Sword", 1))
    conn.commit()
    cur.close()
    conn.close()

    print(f"✓ プレイヤーID: {player_id}")

    # MongoDB: 初期クエスト
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]
    db.quests.insert_one({
        "player_id": player_id,
        "title": "Welcome to the Adventure!",
        "description": "Complete your first battle",
        "status": "active",
        "reward_gold": 50
    })
    print("✓ 初期クエスト追加")
    mongo_client.close()

    # Redis: セッション情報
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.hset(redis_key(f"player:{player_id}"), mapping={
        "name": name,
        "class": player_class,
        "online": "true",
        "last_login": "now"
    })
    print("✓ セッション作成")

    return player_id


def add_item_to_qdrant(item_name, item_type, rarity, description):
    """アイテムをQdrantに追加"""
    qdrant = QdrantClient(url=QDRANT_URL)

    # ダミーベクトル（実際は埋め込みモデルで生成）
    vector = [random.random() for _ in range(128)]

    point_id = random.randint(1, 100000)

    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "name": item_name,
                    "type": item_type,
                    "rarity": rarity,
                    "description": description
                }
            )
        ]
    )
    print(f"✓ アイテム追加: {item_name} (ID: {point_id})")
    return point_id


def search_similar_items(query_item_id):
    """類似アイテム検索"""
    print(f"\n=== 類似アイテム検索 (ID: {query_item_id}) ===")

    qdrant = QdrantClient(url=QDRANT_URL)

    try:
        # アイテム取得
        item = qdrant.retrieve(
            collection_name=QDRANT_COLLECTION,
            ids=[query_item_id],
            with_vectors=True
        )[0]

        # 類似検索
        results = qdrant.query_points(
            collection_name=QDRANT_COLLECTION,
            query=item.vector,
            limit=3
        ).points

        print("\n類似アイテム:")
        for result in results:
            if result.id != query_item_id:
                print(f"  - {result.payload['name']} ({result.payload['rarity']})")
                print(f"    {result.payload['description']}")
                print(f"    類似度スコア: {result.score:.4f}")
    except Exception as e:
        print(f"✗ 検索エラー: {e}")


def display_player_status(player_id):
    """プレイヤーステータス表示"""
    print(f"\n=== プレイヤーステータス (ID: {player_id}) ===")

    # PostgreSQL
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()
    cur.execute("SELECT name, level, hp, mp, gold FROM players WHERE id = %s", (player_id,))
    player = cur.fetchone()

    if player:
        print(f"\n名前: {player[0]}")
        print(f"レベル: {player[1]}")
        print(f"HP: {player[2]}")
        print(f"MP: {player[3]}")
        print(f"ゴールド: {player[4]}")

    # インベントリ
    cur.execute("SELECT item_name, quantity FROM inventory WHERE player_id = %s", (player_id,))
    items = cur.fetchall()
    print("\nインベントリ:")
    for item in items:
        print(f"  - {item[0]} x{item[1]}")

    cur.close()
    conn.close()

    # MongoDB: クエスト
    mongo_client = MongoClient(MONGODB_URL)
    db = mongo_client[APP_NAME]
    quests = list(db.quests.find({"player_id": player_id}))
    print(f"\nクエスト: {len(quests)}件")
    for quest in quests:
        print(f"  - [{quest['status']}] {quest['title']}")
    mongo_client.close()

    # Redis: セッション
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    session = r.hgetall(redis_key(f"player:{player_id}"))
    if session:
        print(f"\nオンライン: {session.get('online', 'false')}")


def main():
    """メイン処理"""
    print("=" * 50)
    print("  RPGゲーム - データベース管理例")
    print("=" * 50)

    # セットアップ
    setup_databases()

    # プレイヤー作成
    player_id = create_player("Hero", "Warrior")

    # アイテム追加
    print("\n=== アイテム追加 ===")
    item1 = add_item_to_qdrant(
        "Steel Sword",
        "weapon",
        "rare",
        "A sturdy sword forged from steel"
    )
    item2 = add_item_to_qdrant(
        "Iron Sword",
        "weapon",
        "common",
        "A basic iron sword"
    )
    item3 = add_item_to_qdrant(
        "Magic Staff",
        "weapon",
        "epic",
        "A staff imbued with magical power"
    )
    add_item_to_qdrant(
        "Wooden Shield",
        "armor",
        "common",
        "A simple wooden shield"
    )

    # 類似アイテム検索
    search_similar_items(item1)

    # ステータス表示
    display_player_status(player_id)

    print("\n" + "=" * 50)
    print("  完了！")
    print("=" * 50)


if __name__ == "__main__":
    main()
