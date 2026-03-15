# アプリ・データベース マッピング情報

**作成者**: Claude Sonnet 4.5 (Anthropic)
**作成日**: 2026年3月9日
**目的**: 他のエージェントが1ファイルで全体像を把握するための完全マッピング

このファイルを読めば、**どのアプリがどのデータベースを使っているか**が一目で分かります。

---

## 📋 目次

1. [全体サマリー](#全体サマリー)
2. [データベース環境](#データベース環境)
3. [現在のアプリ一覧](#現在のアプリ一覧)
4. [データベース別アプリマップ](#データベース別アプリマップ)
5. [アプリ別使用データベース](#アプリ別使用データベース)
6. [接続情報完全リスト](#接続情報完全リスト)
7. [クイックリファレンス表](#クイックリファレンス表)

---

## 🎯 全体サマリー

### 構成

```
1つのDockerデータベース環境
├─ PostgreSQL (1サーバー) → 複数のデータベース
├─ MongoDB (1サーバー) → 複数のデータベース
├─ Redis (1サーバー) → キープレフィックスで分離
└─ Qdrant (1サーバー) → コレクション名で分離
```

### データ分離方法

| データベース | 分離方法 | 例 |
|------------|---------|-----|
| **PostgreSQL** | データベース単位 | `mydb`, `game_rpg`, `app_todo` |
| **MongoDB** | データベース単位 | `mydb`, `game_rpg`, `app_todo` |
| **Redis** | キープレフィックス | `game_rpg:*`, `app_todo:*` |
| **Qdrant** | コレクション名 | `documents`, `game_rpg_items`, `app_todo_vectors` |

---

## 🗄️ データベース環境

### 共通接続情報

| サービス | ホスト | ポート | 接続URL |
|---------|--------|--------|---------|
| PostgreSQL | localhost | 5432 | `postgresql://postgres:postgres@localhost:5432/{DB名}` |
| MongoDB | localhost | 27017 | `mongodb://admin:admin@localhost:27017/{DB名}?authSource=admin` |
| Redis | localhost | 6379 | `redis://localhost:6379` |
| Qdrant | localhost | 6333, 6334 | `http://localhost:6333` (REST), `localhost:6334` (gRPC) |

### 管理UI

| ツール | URL | 対象DB |
|--------|-----|--------|
| **Adminer** | http://localhost:8080 | PostgreSQL |
| **Mongo Express** | http://localhost:8081 | MongoDB |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Qdrant |
| Redis Commander | http://localhost:8082 | Redis (※互換性問題で動作不安定) |

---

## 📱 現在のアプリ一覧

### デフォルトアプリ（初期構築時）

#### 1. **デフォルト環境** (初期サンプル)
- **種類**: サンプル・デモ
- **目的**: 各データベースの動作確認用
- **状態**: ✅ 稼働中

### サンプルアプリ（examples/multi_app/）

#### 2. **game_rpg** - RPGゲーム
- **種類**: ゲーム
- **説明**: ファンタジーRPGのデータ管理
- **サンプルコード**: `examples/multi_app/game1_rpg.py`
- **状態**: ✅ サンプル実装済み

#### 3. **app_todo** - Todoアプリ
- **種類**: アプリ
- **説明**: タスク管理アプリ
- **サンプルコード**: `examples/multi_app/app_todo.py`
- **状態**: ✅ サンプル実装済み

### 追加可能（自動生成スクリプト使用）

```bash
# 新しいアプリを追加
./scripts/add_new_app.sh <app_name> <type>

# 例
./scripts/add_new_app.sh puzzle_game game
./scripts/add_new_app.sh chat_app app
```

---

## 🗺️ データベース別アプリマップ

### PostgreSQL データベース一覧

| データベース名 | 用途 | 使用アプリ | テーブル例 |
|--------------|------|-----------|----------|
| **mydb** | デフォルト・サンプル | 初期環境 | users, documents, products |
| **game_rpg** | RPGゲーム | game_rpg | players, inventory |
| **app_todo** | Todoアプリ | app_todo | users |

**確認コマンド:**
```bash
docker exec local_postgres psql -U postgres -c "\l"
```

---

### MongoDB データベース一覧

| データベース名 | 用途 | 使用アプリ | コレクション例 |
|--------------|------|-----------|--------------|
| **mydb** | デフォルト・サンプル | 初期環境 | users, products |
| **game_rpg** | RPGゲーム | game_rpg | quests, achievements |
| **app_todo** | Todoアプリ | app_todo | todos, projects |

**確認コマンド:**
```bash
docker exec local_mongodb mongosh -u admin -p admin --eval "show dbs"
```

---

### Redis キープレフィックス一覧

| プレフィックス | 用途 | 使用アプリ | キー例 |
|--------------|------|-----------|--------|
| **(なし)** | デフォルト・サンプル | 初期環境 | test_key, message_* |
| **game_rpg:** | RPGゲーム | game_rpg | game_rpg:player:1001, game_rpg:session:* |
| **app_todo:** | Todoアプリ | app_todo | app_todo:user:*, app_todo:stats:* |

**確認コマンド:**
```bash
# 全キー
docker exec local_redis redis-cli KEYS "*"

# プレフィックス別
docker exec local_redis redis-cli KEYS "game_rpg:*"
docker exec local_redis redis-cli KEYS "app_todo:*"
```

---

### Qdrant コレクション一覧

| コレクション名 | 用途 | 使用アプリ | ベクトルサイズ |
|--------------|------|-----------|--------------|
| **documents** | デフォルト・サンプル | 初期環境 | 1536 (OpenAI) |
| **game_rpg_items** | RPGアイテム検索 | game_rpg | 128 |
| **app_todo_vectors** | Todo類似検索 | app_todo | 128 |

**確認コマンド:**
```bash
curl -s http://localhost:6333/collections | jq -r '.result.collections[].name'
```

---

## 🎮 アプリ別使用データベース

### 1. デフォルト環境（初期サンプル）

**使用データベース:**

| DB | データベース/コレクション名 | 用途 |
|----|--------------------------|------|
| PostgreSQL | `mydb` | ユーザー、ドキュメント、商品 |
| MongoDB | `mydb` | ユーザー、商品 |
| Redis | (プレフィックスなし) | テスト用キー |
| Qdrant | `documents` | ドキュメントベクトル検索 |

**サンプルコード:**
- `examples/postgres/python_example.py`
- `examples/mongodb/python_example.py`
- `examples/redis/python_example.py`
- `examples/qdrant/python_example.py`

**接続方法:**
```python
# PostgreSQL
psycopg2.connect("postgresql://postgres:postgres@localhost:5432/mydb")

# MongoDB
MongoClient("mongodb://admin:admin@localhost:27017/").mydb

# Redis
redis.Redis(host='localhost', port=6379)

# Qdrant
QdrantClient(url="http://localhost:6333")
# Collection: "documents"
```

---

### 2. game_rpg - RPGゲーム

**使用データベース:**

| DB | データベース/コレクション名 | 用途 |
|----|--------------------------|------|
| PostgreSQL | `game_rpg` | プレイヤー情報、インベントリ |
| MongoDB | `game_rpg` | クエスト、実績 |
| Redis | `game_rpg:*` | セッション、リアルタイムステータス |
| Qdrant | `game_rpg_items` | アイテム類似検索 |

**データ構造:**

**PostgreSQL:**
- `players` テーブル: id, name, level, hp, mp, gold
- `inventory` テーブル: id, player_id, item_name, quantity

**MongoDB:**
- `quests` コレクション: player_id, title, status, reward_gold
- `achievements` コレクション: player_id, title, unlocked_at

**Redis:**
- `game_rpg:player:{id}` (Hash): name, class, online, last_login
- `game_rpg:session:{id}`: セッション情報
- `game_rpg:score:{id}`: スコア

**Qdrant:**
- Collection: `game_rpg_items`
- Payload: name, type, rarity, description

**サンプルコード:**
```bash
python examples/multi_app/game1_rpg.py
```

**接続方法:**
```python
# PostgreSQL
conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/game_rpg")

# MongoDB
client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
db = client["game_rpg"]

# Redis (キープレフィックス使用)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set("game_rpg:player:1001", "Alice")

# Qdrant
client = QdrantClient(url="http://localhost:6333")
# Collection: "game_rpg_items"
```

---

### 3. app_todo - Todoアプリ

**使用データベース:**

| DB | データベース/コレクション名 | 用途 |
|----|--------------------------|------|
| PostgreSQL | `app_todo` | ユーザー管理 |
| MongoDB | `app_todo` | Todo、プロジェクト |
| Redis | `app_todo:*` | キャッシュ、統計情報 |
| Qdrant | `app_todo_vectors` | Todo類似検索 |

**データ構造:**

**PostgreSQL:**
- `users` テーブル: id, email, name, created_at

**MongoDB:**
- `todos` コレクション: user_id, title, description, status, priority, due_date
- `projects` コレクション: user_id, name, description

**Redis:**
- `app_todo:user:{id}` (Hash): email, name (キャッシュ)
- `app_todo:stats:user:{id}` (Hash): total_todos, pending_todos, completed_todos

**Qdrant:**
- Collection: `app_todo_vectors`
- Payload: todo_id, title, description, priority

**サンプルコード:**
```bash
python examples/multi_app/app_todo.py
```

**接続方法:**
```python
# PostgreSQL
conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/app_todo")

# MongoDB
client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
db = client["app_todo"]

# Redis (キープレフィックス使用)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set("app_todo:user:1", "alice@example.com")

# Qdrant
client = QdrantClient(url="http://localhost:6333")
# Collection: "app_todo_vectors"
```

---

## 🔗 接続情報完全リスト

### PostgreSQL

#### デフォルト環境
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mydb"
```

#### game_rpg
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/game_rpg"
```

#### app_todo
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/app_todo"
```

#### 新しいアプリ追加時
```python
DATABASE_URL = f"postgresql://postgres:postgres@localhost:5432/{APP_NAME}"
```

---

### MongoDB

#### デフォルト環境
```python
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
client = MongoClient(MONGODB_URL)
db = client["mydb"]
```

#### game_rpg
```python
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
client = MongoClient(MONGODB_URL)
db = client["game_rpg"]
```

#### app_todo
```python
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
client = MongoClient(MONGODB_URL)
db = client["app_todo"]
```

#### 新しいアプリ追加時
```python
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
client = MongoClient(MONGODB_URL)
db = client["{APP_NAME}"]
```

---

### Redis

#### 共通接続
```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
```

#### デフォルト環境
```python
r.set("test_key", "value")  # プレフィックスなし
```

#### game_rpg
```python
REDIS_PREFIX = "game_rpg:"
r.set(f"{REDIS_PREFIX}player:1001", "Alice")
```

#### app_todo
```python
REDIS_PREFIX = "app_todo:"
r.set(f"{REDIS_PREFIX}user:1", "alice@example.com")
```

#### 新しいアプリ追加時
```python
REDIS_PREFIX = f"{APP_NAME}:"
r.set(f"{REDIS_PREFIX}key", "value")
```

---

### Qdrant

#### 共通接続
```python
QDRANT_URL = "http://localhost:6333"
client = QdrantClient(url=QDRANT_URL)
```

#### デフォルト環境
```python
COLLECTION_NAME = "documents"
```

#### game_rpg
```python
COLLECTION_NAME = "game_rpg_items"
```

#### app_todo
```python
COLLECTION_NAME = "app_todo_vectors"
```

#### 新しいアプリ追加時
```python
COLLECTION_NAME = f"{APP_NAME}_vectors"
```

---

## 📊 クイックリファレンス表

### 全アプリ・全データベース マップ

| アプリ名 | PostgreSQL | MongoDB | Redis | Qdrant |
|---------|-----------|---------|-------|--------|
| **デフォルト** | `mydb` | `mydb` | (なし) | `documents` |
| **game_rpg** | `game_rpg` | `game_rpg` | `game_rpg:*` | `game_rpg_items` |
| **app_todo** | `app_todo` | `app_todo` | `app_todo:*` | `app_todo_vectors` |

### データベースごとの確認方法

| データベース | 一覧表示コマンド |
|------------|----------------|
| PostgreSQL | `docker exec local_postgres psql -U postgres -c "\l"` |
| MongoDB | `docker exec local_mongodb mongosh -u admin -p admin --eval "show dbs"` |
| Redis | `docker exec local_redis redis-cli KEYS "*"` |
| Qdrant | `curl -s http://localhost:6333/collections \| jq -r '.result.collections[].name'` |

### アプリ追加コマンド

```bash
# 新しいアプリ追加
./scripts/add_new_app.sh <app_name> <type>

# 例
./scripts/add_new_app.sh puzzle_game game
./scripts/add_new_app.sh chat_app app
./scripts/add_new_app.sh api_server service

# 全アプリ一覧表示
./scripts/list_all_apps.sh
```

---

## 🔍 データの探し方

### 特定のアプリのデータを全て確認したい

#### 例: game_rpg のデータを全て見る

```bash
# PostgreSQL
docker exec -it local_postgres psql -U postgres -d game_rpg -c "\dt"

# MongoDB
docker exec -it local_mongodb mongosh -u admin -p admin --eval "use game_rpg; show collections"

# Redis
docker exec local_redis redis-cli KEYS "game_rpg:*"

# Qdrant
curl -s http://localhost:6333/collections/game_rpg_items
```

### 特定のデータベースに何のアプリがあるか確認したい

#### PostgreSQL
```bash
docker exec local_postgres psql -U postgres -c "\l" | grep -v template | grep -v postgres
```

出力例:
```
mydb
game_rpg
app_todo
```

#### MongoDB
```bash
docker exec local_mongodb mongosh -u admin -p admin --quiet --eval "db.adminCommand('listDatabases').databases.forEach(function(d){if (d.name !== 'admin' && d.name !== 'config' && d.name !== 'local') {print(d.name)}})"
```

出力例:
```
mydb
game_rpg
app_todo
```

#### Redis
```bash
docker exec local_redis redis-cli --scan --pattern "*:*" | cut -d: -f1 | sort -u
```

出力例:
```
game_rpg
app_todo
```

#### Qdrant
```bash
curl -s http://localhost:6333/collections | jq -r '.result.collections[].name'
```

出力例:
```
documents
game_rpg_items
app_todo_vectors
```

---

## 🎯 エージェント向けクイックガイド

### このファイルの使い方

1. **全体を把握する**: 「現在のアプリ一覧」セクションを読む
2. **特定のアプリを理解する**: 「アプリ別使用データベース」セクションを読む
3. **接続情報を取得する**: 「接続情報完全リスト」をコピペ
4. **データを確認する**: 「データの探し方」のコマンドを実行

### 新しいアプリを追加する手順

```bash
# 1. 追加スクリプト実行
./scripts/add_new_app.sh my_new_app app

# 2. サンプルコード実行
python examples/multi_app/app_my_new_app.py

# 3. 確認
./scripts/list_all_apps.sh

# 4. このファイル (APP_DATABASE_MAP.md) を更新
#    → 新しいアプリの情報を追加
```

### トラブルシューティング

**問題**: アプリのデータが見つからない

**確認手順**:
1. データベースが存在するか確認
   ```bash
   docker exec local_postgres psql -U postgres -c "\l"
   ```

2. コンテナが起動しているか確認
   ```bash
   docker ps
   ```

3. 接続情報が正しいか確認
   - このファイルの「接続情報完全リスト」を参照

---

## 📝 更新履歴

### 2026-03-09
- 初版作成
- デフォルト環境、game_rpg、app_todo の情報を記載
- 接続情報完全リスト追加
- クイックリファレンス表追加

### 新しいアプリ追加時
このファイルの「現在のアプリ一覧」と「アプリ別使用データベース」セクションを更新してください。

---

## 📞 関連ドキュメント

- **[MULTI_APP_GUIDE.md](./MULTI_APP_GUIDE.md)** - 詳細な管理ガイド
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - プロジェクト全体サマリー
- **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** - Docker操作ガイド
- **[README.md](./README.md)** - プロジェクト概要

---

**作成者**: Claude Sonnet 4.5 (Anthropic)
**最終更新**: 2026年3月9日
**バージョン**: 1.0

**このファイルを他のエージェントに共有すれば、全体像を即座に把握できます！**
