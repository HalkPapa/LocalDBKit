# 複数アプリ・ゲーム管理ガイド

**作成者**: Claude Sonnet 4.5 (Anthropic)
**作成日**: 2026年3月9日
**対象**: 複数のゲーム・アプリで同じデータベース環境を共有したい開発者、AIエージェント

---

## 📋 目次

1. [概要](#概要)
2. [基本コンセプト](#基本コンセプト)
3. [命名規則](#命名規則)
4. [新しいアプリの追加方法](#新しいアプリの追加方法)
5. [データベース別の管理方法](#データベース別の管理方法)
6. [サンプルコード](#サンプルコード)
7. [ベストプラクティス](#ベストプラクティス)
8. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 概要

### できること

この環境では、**1つのデータベース環境で複数のアプリ・ゲームを管理**できます。

```
1つのDocker環境
  ├─ ゲーム1（RPG）
  ├─ ゲーム2（パズル）
  ├─ アプリ1（Todo）
  ├─ アプリ2（チャット）
  └─ ... 無制限に追加可能
```

### メリット

- ✅ 1つの環境で全てのアプリを管理
- ✅ docker-compose up -d で全て起動
- ✅ 1つの管理UIで全データ確認
- ✅ リソース効率的
- ✅ バックアップが簡単

---

## 💡 基本コンセプト

### データベースごとの分離方法

| データベース | 分離方法 | 例 |
|------------|---------|-----|
| **PostgreSQL** | データベース単位で分離 | `game1_db`, `todo_app_db` |
| **MongoDB** | データベース単位で分離 | `game1`, `todo_app` |
| **Redis** | キープレフィックスで分離 | `game1:*`, `todo:*` |
| **Qdrant** | コレクション名で分離 | `game1_items`, `todo_vectors` |

### アーキテクチャ

```
┌──────────────────────────────────────────────┐
│         ローカルデータベース環境              │
├──────────────────────────────────────────────┤
│                                              │
│  PostgreSQL (1サーバー)                      │
│  ├─ game1_rpg      ← ゲーム1                │
│  ├─ game2_puzzle   ← ゲーム2                │
│  ├─ todo_app       ← Todoアプリ             │
│  └─ chat_app       ← チャットアプリ          │
│                                              │
│  MongoDB (1サーバー)                         │
│  ├─ game1_rpg      ← ゲーム1                │
│  ├─ game2_puzzle   ← ゲーム2                │
│  ├─ todo_app       ← Todoアプリ             │
│  └─ chat_app       ← チャットアプリ          │
│                                              │
│  Redis (1サーバー・キープレフィックス分離)    │
│  ├─ game1:*        ← ゲーム1                │
│  ├─ game2:*        ← ゲーム2                │
│  ├─ todo:*         ← Todoアプリ             │
│  └─ chat:*         ← チャットアプリ          │
│                                              │
│  Qdrant (1サーバー・コレクション分離)         │
│  ├─ game1_items    ← ゲーム1                │
│  ├─ game2_levels   ← ゲーム2                │
│  ├─ todo_vectors   ← Todoアプリ             │
│  └─ chat_messages  ← チャットアプリ          │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 📛 命名規則

### 推奨命名規則

#### PostgreSQL / MongoDB データベース名

```
{app_type}_{app_name}

例:
- game_rpg
- game_puzzle
- app_todo
- app_chat
- service_api
```

#### Redis キープレフィックス

```
{app_name}:{data_type}:{id}

例:
- game1:player:1001
- game1:score:1001
- todo:task:abc123
- chat:user:alice
- chat:room:general
```

#### Qdrant コレクション名

```
{app_name}_{data_type}

例:
- game1_items
- game1_characters
- todo_vectors
- chat_messages
```

### 命名規則の重要性

❌ **悪い例**: データベース名が被る
```
mydb  ← 何のアプリ？
game  ← どのゲーム？
app   ← どのアプリ？
```

✅ **良い例**: 一目で分かる
```
game_rpg_fantasy
game_puzzle_blocks
app_todo_personal
```

---

## 🚀 新しいアプリの追加方法

### 自動追加スクリプト

`scripts/add_new_app.sh` を使用:

```bash
# 使い方
./scripts/add_new_app.sh <app_name> <app_type>

# 例: RPGゲームを追加
./scripts/add_new_app.sh rpg_fantasy game

# 例: Todoアプリを追加
./scripts/add_new_app.sh todo_manager app
```

### 手動追加手順

#### 1. PostgreSQLデータベース作成

```bash
# コンテナに入る
docker exec -it local_postgres psql -U postgres

# データベース作成
CREATE DATABASE game_rpg;

# 確認
\l

# 切り替え
\c game_rpg

# テーブル作成
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# 終了
\q
```

#### 2. MongoDBデータベース作成

```bash
# コンテナに入る
docker exec -it local_mongodb mongosh -u admin -p admin

# データベース切り替え（自動作成）
use game_rpg

# コレクション作成とサンプルデータ
db.players.insertOne({
    name: "Hero",
    level: 1,
    class: "Warrior",
    created_at: new Date()
})

# 確認
show dbs
db.players.find()

# 終了
exit
```

#### 3. Redis キープレフィックス使用

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ゲーム1のデータ
r.set("game1:player:1001", "Alice")
r.set("game1:score:1001", "1000")
r.hset("game1:inventory:1001", "sword", "5")

# ゲーム2のデータ
r.set("game2:player:2001", "Bob")
r.set("game2:level:2001", "10")

# パターンマッチで確認
print(r.keys("game1:*"))  # ゲーム1のキー全て
print(r.keys("game2:*"))  # ゲーム2のキー全て
```

#### 4. Qdrant コレクション作成

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url="http://localhost:6333")

# ゲーム1のコレクション
client.create_collection(
    collection_name="game1_items",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# ゲーム2のコレクション
client.create_collection(
    collection_name="game2_levels",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# 確認
collections = client.get_collections()
print([c.name for c in collections.collections])
```

---

## 🗄️ データベース別の管理方法

### PostgreSQL

#### 複数データベースの一覧表示

```bash
docker exec -it local_postgres psql -U postgres -c "\l"
```

#### 特定のデータベースに接続

```bash
# SQLで接続
docker exec -it local_postgres psql -U postgres -d game_rpg

# Pythonで接続
import psycopg2
conn = psycopg2.connect(
    "postgresql://postgres:postgres@localhost:5432/game_rpg"
)
```

#### データベースの削除

```bash
docker exec -it local_postgres psql -U postgres -c "DROP DATABASE game_rpg;"
```

#### データベースのバックアップ

```bash
# 特定のデータベースをバックアップ
docker exec local_postgres pg_dump -U postgres game_rpg > backup_game_rpg.sql

# 全データベースをバックアップ
docker exec local_postgres pg_dumpall -U postgres > backup_all.sql
```

#### データベースのリストア

```bash
cat backup_game_rpg.sql | docker exec -i local_postgres psql -U postgres game_rpg
```

---

### MongoDB

#### 複数データベースの一覧表示

```bash
docker exec -it local_mongodb mongosh -u admin -p admin --eval "show dbs"
```

#### 特定のデータベースに接続

```python
from pymongo import MongoClient

client = MongoClient("mongodb://admin:admin@localhost:27017/")
db = client["game_rpg"]

# コレクション操作
players = db["players"]
players.insert_one({"name": "Hero", "level": 1})
```

#### データベースの削除

```bash
docker exec -it local_mongodb mongosh -u admin -p admin --eval "use game_rpg; db.dropDatabase()"
```

#### データベースのバックアップ

```bash
# 特定のデータベースをバックアップ
docker exec local_mongodb mongodump \
    --username admin --password admin \
    --authenticationDatabase admin \
    --db game_rpg \
    --out /tmp/backup

# バックアップをホストにコピー
docker cp local_mongodb:/tmp/backup ./backup_game_rpg
```

#### データベースのリストア

```bash
# バックアップをコンテナにコピー
docker cp ./backup_game_rpg local_mongodb:/tmp/backup

# リストア
docker exec local_mongodb mongorestore \
    --username admin --password admin \
    --authenticationDatabase admin \
    /tmp/backup
```

---

### Redis

#### キープレフィックスごとのキー一覧

```bash
# ゲーム1のキー全て
docker exec local_redis redis-cli KEYS "game1:*"

# ゲーム2のキー全て
docker exec local_redis redis-cli KEYS "game2:*"

# 全キー
docker exec local_redis redis-cli KEYS "*"
```

#### 特定のプレフィックスのキーを削除

```bash
# ゲーム1のデータを全削除
docker exec local_redis redis-cli --scan --pattern "game1:*" | xargs docker exec -i local_redis redis-cli DEL

# または Pythonで
import redis
r = redis.Redis(host='localhost', port=6379)
keys = r.keys("game1:*")
if keys:
    r.delete(*keys)
```

#### キーの総数確認

```bash
docker exec local_redis redis-cli DBSIZE
```

#### バックアップ

```bash
# RDBファイルを保存
docker exec local_redis redis-cli SAVE

# バックアップファイルをコピー
docker cp local_redis:/data/dump.rdb ./backup_redis.rdb
```

---

### Qdrant

#### コレクション一覧

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
collections = client.get_collections()
print([c.name for c in collections.collections])
```

#### 特定のコレクションに接続

```python
# ゲーム1のアイテムコレクション
from qdrant_client.models import PointStruct

points = [
    PointStruct(
        id=1,
        vector=[0.1] * 384,
        payload={"name": "Sword", "rarity": "rare"}
    )
]

client.upsert(
    collection_name="game1_items",
    points=points
)
```

#### コレクションの削除

```python
client.delete_collection("game1_items")
```

#### コレクションのバックアップ

```bash
# スナップショット作成
curl -X POST "http://localhost:6333/collections/game1_items/snapshots"

# スナップショット一覧
curl "http://localhost:6333/collections/game1_items/snapshots"

# ダウンロード
curl "http://localhost:6333/collections/game1_items/snapshots/{snapshot_name}" \
    -o backup_game1_items.snapshot
```

---

## 💻 サンプルコード

サンプルコードは `examples/multi_app/` にあります:

- **game1_rpg.py** - RPGゲームの例
- **game2_puzzle.py** - パズルゲームの例
- **app_todo.py** - Todoアプリの例
- **app_chat.py** - チャットアプリの例

### 使い方

```bash
# 依存関係インストール（既に完了している場合はスキップ）
pip install -r requirements.txt

# RPGゲームのサンプル実行
python examples/multi_app/game1_rpg.py

# Todoアプリのサンプル実行
python examples/multi_app/app_todo.py
```

---

## 📚 ベストプラクティス

### 1. 命名規則を統一

```python
# ✅ 良い例
DATABASE_NAME = "game_rpg"
REDIS_PREFIX = "game_rpg"
QDRANT_COLLECTION = "game_rpg_items"

# ❌ 悪い例
DATABASE_NAME = "mydb"
REDIS_PREFIX = "g1"
QDRANT_COLLECTION = "items"
```

### 2. 環境変数で管理

```python
# config.py
import os

class GameRPGConfig:
    DB_URL = os.getenv(
        "GAME_RPG_DB_URL",
        "postgresql://postgres:postgres@localhost:5432/game_rpg"
    )
    REDIS_PREFIX = "game_rpg"
    MONGODB_DB = "game_rpg"
    QDRANT_COLLECTION = "game_rpg_items"
```

### 3. 接続を再利用

```python
# db_manager.py
import psycopg2
from pymongo import MongoClient
import redis
from qdrant_client import QdrantClient

class DatabaseManager:
    def __init__(self, app_name):
        self.app_name = app_name

        # PostgreSQL
        self.pg_conn = psycopg2.connect(
            f"postgresql://postgres:postgres@localhost:5432/{app_name}"
        )

        # MongoDB
        self.mongo_client = MongoClient(
            "mongodb://admin:admin@localhost:27017/"
        )
        self.mongo_db = self.mongo_client[app_name]

        # Redis
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.redis_prefix = f"{app_name}:"

        # Qdrant
        self.qdrant = QdrantClient(url="http://localhost:6333")
        self.qdrant_collection = f"{app_name}_vectors"

    def redis_key(self, key):
        return f"{self.redis_prefix}{key}"

    def close(self):
        self.pg_conn.close()
        self.mongo_client.close()

# 使用例
db = DatabaseManager("game_rpg")
db.redis.set(db.redis_key("player:1001"), "Alice")
db.close()
```

### 4. データの分離を徹底

```python
# ✅ 良い例: 完全に分離
game1_db = DatabaseManager("game1_rpg")
game2_db = DatabaseManager("game2_puzzle")

game1_db.redis.set(game1_db.redis_key("score"), "100")
game2_db.redis.set(game2_db.redis_key("score"), "200")

# ❌ 悪い例: 混在
redis_client = redis.Redis()
redis_client.set("score", "100")  # どのゲーム？
```

### 5. バックアップを定期的に

```bash
# backup_all_apps.sh
#!/bin/bash

BACKUP_DIR="./backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# PostgreSQL: 全データベース
docker exec local_postgres pg_dumpall -U postgres > "$BACKUP_DIR/postgres_all.sql"

# MongoDB: 全データベース
docker exec local_mongodb mongodump \
    --username admin --password admin \
    --authenticationDatabase admin \
    --out /tmp/backup
docker cp local_mongodb:/tmp/backup "$BACKUP_DIR/mongodb"

# Redis
docker exec local_redis redis-cli SAVE
docker cp local_redis:/data/dump.rdb "$BACKUP_DIR/redis.rdb"

echo "Backup completed: $BACKUP_DIR"
```

---

## 🐛 トラブルシューティング

### 問題1: データベースが見つからない

**症状**:
```
psycopg2.OperationalError: FATAL: database "game_rpg" does not exist
```

**原因**: データベースがまだ作成されていない

**解決**:
```bash
docker exec -it local_postgres psql -U postgres -c "CREATE DATABASE game_rpg;"
```

---

### 問題2: Redisキーが混在

**症状**: 別のアプリのデータが取得される

**原因**: キープレフィックスを使用していない

**解決**:
```python
# ❌ 悪い例
redis.set("player", "Alice")

# ✅ 良い例
redis.set("game1:player", "Alice")
redis.set("game2:player", "Bob")
```

---

### 問題3: MongoDBの認証エラー

**症状**:
```
pymongo.errors.OperationFailure: Authentication failed
```

**原因**: authSource指定忘れ

**解決**:
```python
# ✅ 正しい接続
client = MongoClient(
    "mongodb://admin:admin@localhost:27017/?authSource=admin"
)
```

---

### 問題4: Qdrantコレクションが既に存在

**症状**:
```
ValueError: Collection game1_items already exists
```

**原因**: 同名のコレクションが既に存在

**解決**:
```python
# 存在チェックしてから作成
try:
    client.get_collection("game1_items")
    print("Collection already exists")
except:
    client.create_collection("game1_items", ...)
```

---

### 問題5: データベースが多すぎて遅い

**症状**: 起動やクエリが遅い

**原因**: リソース不足

**解決**:
1. **不要なデータベース削除**
2. **Colimaのリソース増強**
   ```bash
   colima stop
   colima start --disk 100 --cpu 6 --memory 12
   ```
3. **データベースを分割** - 複数のDocker環境に分ける

---

## 📊 管理UIでの確認

### Adminer (PostgreSQL)

http://localhost:8080

1. ログイン
2. 左上のドロップダウンでデータベース切り替え
   - `game_rpg`
   - `game_puzzle`
   - `todo_app`
   - etc.

### Mongo Express (MongoDB)

http://localhost:8081

- 左サイドバーに全データベースが表示
- クリックして切り替え

### Qdrant Dashboard

http://localhost:6333/dashboard

- Collections タブで全コレクション表示
- 各コレクションをクリックして詳細確認

---

## 🔍 現在のアプリ一覧確認

### 全データベース一覧スクリプト

```bash
#!/bin/bash
# list_all_apps.sh

echo "=== PostgreSQL Databases ==="
docker exec local_postgres psql -U postgres -c "\l" | grep -v template | grep -v postgres

echo ""
echo "=== MongoDB Databases ==="
docker exec local_mongodb mongosh -u admin -p admin --quiet --eval "db.adminCommand('listDatabases').databases.forEach(function(d){print(d.name)})"

echo ""
echo "=== Redis Key Prefixes ==="
docker exec local_redis redis-cli --scan --pattern "*:*" | cut -d: -f1 | sort -u

echo ""
echo "=== Qdrant Collections ==="
curl -s http://localhost:6333/collections | jq -r '.result.collections[].name'
```

実行:
```bash
chmod +x scripts/list_all_apps.sh
./scripts/list_all_apps.sh
```

---

## 📝 エージェント向けクイックリファレンス

### 新しいアプリ追加（完全手順）

```bash
# 1. PostgreSQLデータベース作成
docker exec -it local_postgres psql -U postgres -c "CREATE DATABASE app_name;"

# 2. MongoDBは自動作成（コード内で初回アクセス時）

# 3. Redisはキープレフィックス使用（app_name:*）

# 4. Qdrantコレクション作成（Pythonコード内）

# 5. サンプルコードを examples/multi_app/ に追加

# 6. テスト実行
python examples/multi_app/app_name.py
```

### データベース接続テンプレート

```python
import psycopg2
from pymongo import MongoClient
import redis
from qdrant_client import QdrantClient

APP_NAME = "your_app_name"

# PostgreSQL
pg_conn = psycopg2.connect(
    f"postgresql://postgres:postgres@localhost:5432/{APP_NAME}"
)

# MongoDB
mongo_client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
mongo_db = mongo_client[APP_NAME]

# Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
REDIS_PREFIX = f"{APP_NAME}:"

# Qdrant
qdrant_client = QdrantClient(url="http://localhost:6333")
QDRANT_COLLECTION = f"{APP_NAME}_vectors"
```

---

## 🎯 まとめ

### このガイドでできること

✅ 複数のアプリ・ゲームを1つのDB環境で管理
✅ 新しいアプリの追加
✅ 各データベースでのデータ分離
✅ バックアップ・リストア
✅ トラブルシューティング

### 次のステップ

1. **サンプルコードを実行** - `examples/multi_app/`
2. **自分のアプリを追加** - `scripts/add_new_app.sh` 使用
3. **定期バックアップ設定** - cron設定

---

**作成者**: Claude Sonnet 4.5 (Anthropic)
**最終更新**: 2026年3月9日
**バージョン**: 1.0
