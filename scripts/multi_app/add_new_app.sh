#!/bin/bash

# 新しいアプリ・ゲーム追加スクリプト
# 作成者: Claude Sonnet 4.5 (Anthropic)
# 作成日: 2026年3月9日

set -e

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルプメッセージ
show_help() {
    echo "使い方: $0 <app_name> <app_type>"
    echo ""
    echo "引数:"
    echo "  app_name   アプリ名（英数字とアンダースコアのみ）"
    echo "  app_type   アプリの種類 (game/app/service)"
    echo ""
    echo "例:"
    echo "  $0 rpg_fantasy game"
    echo "  $0 todo_manager app"
    echo "  $0 api_server service"
    echo ""
    exit 1
}

# 引数チェック
if [ $# -ne 2 ]; then
    echo -e "${RED}エラー: 引数が不足しています${NC}"
    show_help
fi

APP_NAME=$1
APP_TYPE=$2

# アプリ名の検証
if [[ ! "$APP_NAME" =~ ^[a-z0-9_]+$ ]]; then
    echo -e "${RED}エラー: アプリ名は英小文字、数字、アンダースコアのみ使用できます${NC}"
    exit 1
fi

# アプリタイプの検証
if [[ ! "$APP_TYPE" =~ ^(game|app|service)$ ]]; then
    echo -e "${RED}エラー: app_typeは game, app, service のいずれかを指定してください${NC}"
    exit 1
fi

# データベース名
DB_NAME="${APP_TYPE}_${APP_NAME}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  新しいアプリ追加: ${APP_NAME}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "アプリ名: ${GREEN}${APP_NAME}${NC}"
echo -e "種類: ${GREEN}${APP_TYPE}${NC}"
echo -e "データベース名: ${GREEN}${DB_NAME}${NC}"
echo ""

# 確認
read -p "続行しますか? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}キャンセルしました${NC}"
    exit 0
fi

# PostgreSQLデータベース作成
echo ""
echo -e "${BLUE}[1/4] PostgreSQLデータベース作成中...${NC}"
if docker exec local_postgres psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo -e "${YELLOW}  ⚠ データベース '$DB_NAME' は既に存在します（スキップ）${NC}"
else
    docker exec local_postgres psql -U postgres -c "CREATE DATABASE $DB_NAME;"
    echo -e "${GREEN}  ✓ PostgreSQLデータベース作成完了${NC}"
fi

# MongoDBデータベース初期化
echo ""
echo -e "${BLUE}[2/4] MongoDBデータベース初期化中...${NC}"
docker exec local_mongodb mongosh -u admin -p admin --quiet --eval "
use $DB_NAME;
db.createCollection('_init');
db._init.insertOne({created_at: new Date(), note: 'Initialized by add_new_app.sh'});
print('MongoDB database initialized');
" > /dev/null 2>&1
echo -e "${GREEN}  ✓ MongoDBデータベース初期化完了${NC}"

# Redisキープレフィックスの説明
echo ""
echo -e "${BLUE}[3/4] Redis設定...${NC}"
echo -e "${GREEN}  ✓ Redisキープレフィックス: ${DB_NAME}:*${NC}"
echo -e "    例: ${DB_NAME}:user:1001"

# Qdrantコレクションの説明
echo ""
echo -e "${BLUE}[4/4] Qdrant設定...${NC}"
echo -e "${GREEN}  ✓ Qdrantコレクション名: ${DB_NAME}_vectors${NC}"
echo -e "    ※コレクション作成はPythonコード内で実行してください"

# サンプルコード作成
echo ""
echo -e "${BLUE}サンプルコード作成中...${NC}"

SAMPLE_FILE="examples/multi_app/${APP_TYPE}_${APP_NAME}.py"
mkdir -p "examples/multi_app"

cat > "$SAMPLE_FILE" << 'EOFPYTHON'
#!/usr/bin/env python3
"""
{APP_TYPE}_{APP_NAME} サンプルコード
作成者: Claude Sonnet 4.5 (Anthropic)
自動生成日: $(date +%Y-%m-%d)

このファイルは複数のデータベースを使用する例です。
"""

import psycopg2
from pymongo import MongoClient
import redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import sys

# 設定
APP_NAME = "{APP_NAME}"
DB_NAME = "{DB_NAME}"

# データベース接続情報
POSTGRES_URL = f"postgresql://postgres:postgres@localhost:5432/{DB_NAME}"
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
QDRANT_URL = "http://localhost:6333"

# Redisキープレフィックス
REDIS_PREFIX = f"{DB_NAME}:"

# Qdrantコレクション名
QDRANT_COLLECTION = f"{DB_NAME}_vectors"


def redis_key(key):
    """Redisキーにプレフィックスを追加"""
    return f"{REDIS_PREFIX}{key}"


def setup_postgresql():
    """PostgreSQLのテーブル作成"""
    print("\n=== PostgreSQL セットアップ ===")
    try:
        conn = psycopg2.connect(POSTGRES_URL)
        cur = conn.cursor()

        # テーブル作成
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # サンプルデータ挿入
        cur.execute("""
            INSERT INTO users (name, email)
            VALUES (%s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (f"{APP_NAME}_user", f"{APP_NAME}@example.com"))

        conn.commit()

        # 確認
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        print(f"✓ PostgreSQLテーブル作成完了")
        print(f"  ユーザー数: {len(users)}")

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ PostgreSQLエラー: {e}")
        return False


def setup_mongodb():
    """MongoDBのコレクション作成"""
    print("\n=== MongoDB セットアップ ===")
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DB_NAME]

        # コレクション作成とサンプルデータ
        collection = db["items"]

        # サンプルデータ挿入
        collection.insert_one({
            "name": f"{APP_NAME}_item",
            "category": "{APP_TYPE}",
            "count": 1
        })

        # 確認
        count = collection.count_documents({})
        print(f"✓ MongoDBコレクション作成完了")
        print(f"  ドキュメント数: {count}")

        client.close()
        return True
    except Exception as e:
        print(f"✗ MongoDBエラー: {e}")
        return False


def setup_redis():
    """Redisキーの作成"""
    print("\n=== Redis セットアップ ===")
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        # サンプルデータ設定
        r.set(redis_key("status"), "active")
        r.set(redis_key("version"), "1.0.0")
        r.hset(redis_key("config"), mapping={
            "max_users": "1000",
            "timeout": "3600"
        })

        # 確認
        keys = r.keys(f"{REDIS_PREFIX}*")
        print(f"✓ Redisキー作成完了")
        print(f"  キー数: {len(keys)}")
        print(f"  キープレフィックス: {REDIS_PREFIX}")

        return True
    except Exception as e:
        print(f"✗ Redisエラー: {e}")
        return False


def setup_qdrant():
    """Qdrantコレクションの作成"""
    print("\n=== Qdrant セットアップ ===")
    try:
        client = QdrantClient(url=QDRANT_URL)

        # コレクション存在チェック
        try:
            client.get_collection(QDRANT_COLLECTION)
            print(f"⚠ コレクション '{QDRANT_COLLECTION}' は既に存在します")
        except:
            # コレクション作成
            client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"✓ Qdrantコレクション作成完了")

        # サンプルベクトル追加
        points = [
            PointStruct(
                id=1,
                vector=[0.1] * 384,
                payload={"name": f"{APP_NAME}_vector_1", "type": "{APP_TYPE}"}
            )
        ]

        client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=points
        )

        # 確認
        collection_info = client.get_collection(QDRANT_COLLECTION)
        print(f"  コレクション名: {QDRANT_COLLECTION}")
        print(f"  ベクトル数: {collection_info.points_count}")

        return True
    except Exception as e:
        print(f"✗ Qdrantエラー: {e}")
        return False


def main():
    """メイン処理"""
    print("=" * 50)
    print(f"  {DB_NAME} セットアップ")
    print("=" * 50)

    results = []

    # PostgreSQL
    results.append(("PostgreSQL", setup_postgresql()))

    # MongoDB
    results.append(("MongoDB", setup_mongodb()))

    # Redis
    results.append(("Redis", setup_redis()))

    # Qdrant
    results.append(("Qdrant", setup_qdrant()))

    # 結果サマリー
    print("\n" + "=" * 50)
    print("  結果サマリー")
    print("=" * 50)
    for name, success in results:
        status = "✓ 成功" if success else "✗ 失敗"
        print(f"{name:15s}: {status}")

    # 成功した数
    success_count = sum(1 for _, success in results if success)
    print(f"\n成功: {success_count}/{len(results)}")

    if success_count == len(results):
        print("\n🎉 全てのデータベースのセットアップが完了しました！")
        return 0
    else:
        print("\n⚠ 一部のデータベースのセットアップに失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
EOFPYTHON

# プレースホルダー置換
sed -i '' "s/{APP_NAME}/$APP_NAME/g" "$SAMPLE_FILE"
sed -i '' "s/{DB_NAME}/$DB_NAME/g" "$SAMPLE_FILE"
sed -i '' "s/{APP_TYPE}/$APP_TYPE/g" "$SAMPLE_FILE"

chmod +x "$SAMPLE_FILE"

echo -e "${GREEN}  ✓ サンプルコード作成: $SAMPLE_FILE${NC}"

# 完了
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ セットアップ完了！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo ""
echo -e "1. サンプルコードを実行:"
echo -e "   ${YELLOW}python $SAMPLE_FILE${NC}"
echo ""
echo -e "2. Adminerで確認 (PostgreSQL):"
echo -e "   ${YELLOW}http://localhost:8080${NC}"
echo -e "   Database: ${GREEN}$DB_NAME${NC}"
echo ""
echo -e "3. Mongo Expressで確認 (MongoDB):"
echo -e "   ${YELLOW}http://localhost:8081${NC}"
echo -e "   Database: ${GREEN}$DB_NAME${NC}"
echo ""
echo -e "4. Qdrant Dashboardで確認:"
echo -e "   ${YELLOW}http://localhost:6333/dashboard${NC}"
echo -e "   Collection: ${GREEN}${DB_NAME}_vectors${NC}"
echo ""
