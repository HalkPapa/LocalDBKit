# クイックスタートガイド

## 🚀 5分で始めるローカルDB環境

### ステップ1: Docker環境のセットアップ

まず、Docker環境がインストールされているか確認:
```bash
docker --version
```

#### パターンA: Docker環境がない場合

**オプション1: Colima（推奨・軽量）**
```bash
# インストール
brew install colima docker docker-compose

# 起動
colima start

# 確認
docker ps
```

**オプション2: Docker Desktop**
```bash
# インストール
brew install --cask docker

# アプリケーションフォルダから「Docker.app」を起動
open -a Docker
```

#### パターンB: Docker環境がある場合

Dockerデーモンが起動しているか確認:
```bash
docker ps
```

エラーが出る場合は、Docker Desktop または Colima を起動:
```bash
# Docker Desktopの場合
open -a Docker

# Colimaの場合
colima start
```

### ステップ2: データベース起動

```bash
# このディレクトリに移動
cd /path/to/データベース構築

# 起動スクリプトを実行
./start.sh

# または直接docker-composeを実行
docker-compose up -d

# 起動には初回1〜2分、2回目以降は数秒かかります
```

### ステップ3: 動作確認

ブラウザで以下のURLにアクセス:
- **Adminer**: http://localhost:8080
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### ステップ4: サンプルコードを実行

#### Python環境のセットアップ
```bash
# 依存関係をインストール
pip install -r requirements.txt

# PostgreSQLの例を実行
python examples/postgres/python_example.py

# Redisの例を実行
python examples/redis/python_example.py

# MongoDBの例を実行
python examples/mongodb/python_example.py

# Qdrantの例を実行
python examples/qdrant/python_example.py
```

#### Node.js環境のセットアップ
```bash
# 依存関係をインストール
npm install

# PostgreSQLの例を実行
node examples/postgres/nodejs_example.js
```

---

## 📊 各データベースへの接続テスト

### PostgreSQL

#### psqlコマンドラインで接続
```bash
docker exec -it local_postgres psql -U postgres -d mydb
```

#### SQL実行例
```sql
-- テーブル一覧
\dt

-- ユーザー一覧
SELECT * FROM users;

-- ベクトル拡張の確認
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 終了
\q
```

### Redis

#### redis-cliで接続
```bash
docker exec -it local_redis redis-cli
```

#### コマンド例
```bash
# 接続テスト
PING

# キーと値を保存
SET mykey "Hello Redis"
GET mykey

# 全キーの確認
KEYS *

# 終了
exit
```

### MongoDB

#### mongoshで接続
```bash
docker exec -it local_mongodb mongosh -u admin -p admin
```

#### コマンド例
```javascript
// データベース一覧
show dbs

// データベース切り替え
use mydb

// コレクション一覧
show collections

// ドキュメント検索
db.users.find()

// 終了
exit
```

### Qdrant

#### REST APIでテスト
```bash
# コレクション一覧
curl http://localhost:6333/collections

# ヘルスチェック
curl http://localhost:6333/health
```

---

## 🛠️ よく使うコマンド

### サービス管理
```bash
# 起動
docker-compose up -d

# 停止
docker-compose down

# 再起動
docker-compose restart

# 状態確認
docker-compose ps

# ログ確認
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f postgres
```

### データリセット
```bash
# 全データを削除して再起動
docker-compose down -v
docker-compose up -d
```

### 個別サービスの再起動
```bash
# PostgreSQLのみ再起動
docker-compose restart postgres

# Redisのみ再起動
docker-compose restart redis
```

---

## 💡 次のステップ

### 1. Adminerでデータベースを操作
http://localhost:8080 にアクセス

**PostgreSQL接続情報:**
- System: PostgreSQL
- Server: postgres
- Username: postgres
- Password: postgres
- Database: mydb

### 2. ベクトル検索を試す

#### PostgreSQL + pgvector
```python
# examples/postgres/python_example.py を参照
# OpenAI APIで実際の埋め込みベクトルを生成して試すことも可能
```

#### Qdrant
```python
# examples/qdrant/python_example.py を参照
# Sentence Transformersなどで実際のベクトルを生成推奨
```

### 3. 実際のアプリケーションに統合

`.env.example` をコピーして `.env` を作成:
```bash
cp .env.example .env
```

アプリケーションから接続文字列を使用:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
MONGODB_URL = os.getenv("MONGODB_URL")
```

---

## 🔧 トラブルシューティング

### ポートが既に使用されている

エラー: `Bind for 0.0.0.0:5432 failed: port is already allocated`

**解決方法:**
1. 使用中のプロセスを確認
   ```bash
   lsof -i :5432
   ```

2. docker-compose.yml のポート番号を変更
   ```yaml
   ports:
     - "15432:5432"  # ホスト側のポートを変更
   ```

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs postgres

# コンテナを完全に削除して再作成
docker-compose down -v
docker-compose up -d
```

### データが保存されない

Volumeがマウントされているか確認:
```bash
docker volume ls
docker-compose down -v  # Volume削除
docker-compose up -d    # 再作成
```

---

## 📚 さらに学ぶ

- [README.md](./README.md) - 詳細な接続情報
- [DATABASES.md](./DATABASES.md) - 各DBの使い分けガイド
- 公式ドキュメント:
  - [PostgreSQL](https://www.postgresql.org/docs/)
  - [pgvector](https://github.com/pgvector/pgvector)
  - [Redis](https://redis.io/docs/)
  - [MongoDB](https://www.mongodb.com/docs/)
  - [Qdrant](https://qdrant.tech/documentation/)

---

Happy Coding! 🎉
