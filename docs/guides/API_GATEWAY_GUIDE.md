# API Gateway ユーザーガイド

LocalDBKit API Gatewayの使用方法を説明します。

## 📖 概要

API Gatewayは、LocalDBKitの全てのバックエンドサービス（PostgreSQL、MongoDB、Redis、Qdrant、Ollama）への統一されたアクセスポイントを提供します。

**主な機能**:
- JWT認証によるセキュアなアクセス
- レート制限によるAPI保護
- Swagger UIによる自動ドキュメント生成
- 全サービスへの統一APIエンドポイント

## 🚀 クイックスタート

### 1. API Gateway起動

```bash
# 全サービス起動（API Gateway含む）
make up

# API Gatewayのみ起動
docker compose up -d api-gateway

# 起動確認
curl http://localhost:8000/health
```

**レスポンス例**:
```json
{
  "status": "healthy",
  "version": "0.3.0"
}
```

### 2. Swagger UIでAPIを確認

ブラウザで以下のURLを開く:
```
http://localhost:8000/api/v1/docs
```

インタラクティブなAPIドキュメントが表示され、各エンドポイントをテストできます。

## 🔐 認証

### JWT認証フロー

#### 1. ログイン（トークン取得）

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

**レスポンス**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### 2. トークンを使用してAPIにアクセス

```bash
# トークンを変数に保存
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 認証が必要なエンドポイントにアクセス
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/databases/status
```

#### 3. ユーザー情報確認

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

**レスポンス**:
```json
{
  "username": "admin",
  "email": "admin@localdbkit.local",
  "full_name": "Administrator",
  "disabled": false
}
```

### デフォルト認証情報

- **ユーザー名**: `admin`
- **パスワード**: `admin`

⚠️ **本番環境では必ず変更してください！**

## 📡 APIエンドポイント

### 認証 (`/api/v1/auth`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| POST | `/auth/login` | ログイン、JWTトークン取得 | 不要 |
| GET | `/auth/me` | 現在のユーザー情報取得 | 必要 |
| POST | `/auth/logout` | ログアウト | 必要 |

### データベース (`/api/v1/databases`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/databases/status` | 全データベース状態 | 必要 |
| GET | `/databases/postgres/tables` | PostgreSQLテーブル一覧 | 必要 |
| GET | `/databases/mongodb/collections` | MongoDBコレクション一覧 | 必要 |
| GET | `/databases/redis/keys` | Redisキー一覧 | 必要 |
| GET | `/databases/qdrant/collections` | Qdrantコレクション一覧 | 必要 |

### LLM (`/api/v1/llm`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/llm/models` | 利用可能モデル一覧 | 必要 |
| POST | `/llm/chat` | チャット（ストリーミング対応） | 必要 |
| POST | `/llm/embeddings` | テキスト埋め込み生成 | 必要 |
| POST | `/llm/models/pull` | モデルダウンロード | 必要 |

### RAG (`/api/v1/rag`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| POST | `/rag/query` | RAGクエリ | 必要 |
| POST | `/rag/documents` | ドキュメント追加 | 必要 |
| GET | `/rag/documents` | ドキュメント一覧 | 必要 |
| DELETE | `/rag/documents/:id` | ドキュメント削除 | 必要 |
| GET | `/rag/collections` | コレクション一覧 | 必要 |

## 💻 使用例

### データベース状態確認

```bash
# 1. ログイン
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin" | jq -r '.access_token')

# 2. データベース状態取得
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/databases/status | jq
```

**レスポンス**:
```json
[
  {
    "name": "PostgreSQL",
    "status": "healthy",
    "url": "postgres:5432"
  },
  {
    "name": "MongoDB",
    "status": "healthy",
    "url": "mongodb:27017"
  },
  {
    "name": "Redis",
    "status": "healthy",
    "url": "redis:6379"
  },
  {
    "name": "Qdrant",
    "status": "healthy",
    "url": "qdrant:6333"
  }
]
```

### LLMモデル一覧取得

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/llm/models | jq
```

### LLMチャット（予定）

```bash
curl -X POST http://localhost:8000/api/v1/llm/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma2:9b",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ],
    "stream": false
  }' | jq
```

### RAGクエリ（予定）

```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pgvectorとは何ですか？",
    "top_k": 5,
    "collection": "knowledge_base"
  }' | jq
```

## 🛡️ セキュリティ

### レート制限

APIは以下のレート制限が設定されています：

| エンドポイント | 制限 |
|----------------|------|
| `/auth/login` | 5 req/分 |
| `/llm/chat` | 10 req/分 |
| その他 | 60 req/分 |

制限超過時のレスポンス:
```json
{
  "error": "Rate limit exceeded"
}
```

### JWT設定

- **アルゴリズム**: HS256
- **有効期限**: 1時間（アクセストークン）
- **シークレットキー**: 環境変数 `JWT_SECRET_KEY` で設定

⚠️ **本番環境では強力なランダムキーを設定してください**

```bash
# 強力なシークレットキー生成例
openssl rand -hex 32
```

## 🔧 設定

### 環境変数

API Gatewayは以下の環境変数で設定できます（`.env`ファイル）：

```env
# セキュリティ
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# レート制限
REDIS_HOST=redis
REDIS_PORT=6379
RATE_LIMIT_DEFAULT=60/minute
RATE_LIMIT_AUTH=5/minute
RATE_LIMIT_LLM=10/minute

# バックエンドサービス
POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/mydb
MONGODB_URL=mongodb://admin:admin@mongodb:27017
OLLAMA_URL=http://ollama:11434
QDRANT_URL=http://qdrant:6333
```

### docker-compose.yml設定

```yaml
api-gateway:
  build: ./apps/api-gateway
  container_name: local_api_gateway
  ports:
    - "8000:8000"
  environment:
    - JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-secret-key}
  depends_on:
    - redis
    - postgres
    - mongodb
    - ollama
    - qdrant
```

## 🧪 テスト

### ヘルスチェック

```bash
# ヘルスチェック
curl http://localhost:8000/health

# ルートエンドポイント
curl http://localhost:8000/
```

### Swagger UIでテスト

1. ブラウザで http://localhost:8000/api/v1/docs を開く
2. 「Authorize」ボタンをクリック
3. ログインエンドポイントでトークンを取得
4. トークンを入力して「Authorize」
5. 各エンドポイントをテスト

## 📊 監視

### ログ確認

```bash
# API Gatewayログ
docker logs local_api_gateway

# リアルタイムログ
docker logs -f local_api_gateway
```

### メトリクス

API Gatewayのメトリクスは、Prometheus経由でGrafanaで確認できます（今後実装予定）。

## ❓ トラブルシューティング

### API Gatewayが起動しない

```bash
# ログ確認
docker logs local_api_gateway

# コンテナ状態確認
docker compose ps api-gateway

# 再起動
docker compose restart api-gateway
```

### 認証エラー（401 Unauthorized）

- トークンの有効期限を確認（1時間）
- トークンが正しくヘッダーに設定されているか確認
- `Authorization: Bearer <token>` 形式を使用

### レート制限エラー（429 Too Many Requests）

- 制限がリセットされるまで待つ（1分）
- または、`.env`でレート制限を調整

### CORS エラー

デフォルトで以下のオリジンが許可されています：
- `http://localhost:3000`
- `http://localhost:8080`
- `http://localhost:8081`

追加のオリジンを許可するには、`config.py`の`cors_origins`を編集してください。

## 🔗 関連ドキュメント

- [API設計ドキュメント](../../apps/api-gateway/API_DESIGN.md)
- [Docker ガイド](DOCKER_GUIDE.md)
- [セキュリティガイド](../reference/SECURITY.md)（予定）

---

**作成日**: 2026-03-16
**最終更新**: 2026-03-16
**バージョン**: 0.3.0
