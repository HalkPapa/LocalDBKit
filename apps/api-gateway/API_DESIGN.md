# API Gateway 設計ドキュメント

## 概要

LocalDBKit用の統一APIゲートウェイ。全てのバックエンドサービスへのアクセスを一元化し、認証・レート制限・ドキュメント生成を提供します。

## アーキテクチャ

```
┌─────────┐
│ Client  │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────┐
│      API Gateway (FastAPI)          │
│  ┌─────────┐  ┌──────────────┐    │
│  │  JWT    │  │ Rate Limiting│    │
│  │  Auth   │  │   (Redis)    │    │
│  └─────────┘  └──────────────┘    │
│  ┌─────────────────────────────┐  │
│  │      Swagger UI             │  │
│  └─────────────────────────────┘  │
└────┬────────────────────────────┬──┘
     │                            │
     ▼                            ▼
┌──────────┐              ┌──────────┐
│PostgreSQL│              │  Ollama  │
│ MongoDB  │              │  Qdrant  │
│  Redis   │              │   RAG    │
└──────────┘              └──────────┘
```

## エンドポイント構造

### ベースURL

```
http://localhost:8000/api/v1
```

### エンドポイント一覧

#### 1. 認証 (`/auth`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| POST | `/auth/login` | ログイン、JWTトークン取得 | 不要 |
| POST | `/auth/refresh` | トークンリフレッシュ | 必要 |
| POST | `/auth/logout` | ログアウト | 必要 |

**リクエスト例 (Login)**:
```json
{
  "username": "admin",
  "password": "secret"
}
```

**レスポンス例**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### 2. データベース管理 (`/databases`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/databases/status` | 全データベース状態 | 必要 |
| GET | `/databases/postgres/query` | PostgreSQL クエリ | 必要 |
| POST | `/databases/mongodb/query` | MongoDB クエリ | 必要 |
| GET | `/databases/redis/get/:key` | Redis取得 | 必要 |
| POST | `/databases/redis/set` | Redis設定 | 必要 |
| GET | `/databases/qdrant/collections` | Qdrantコレクション一覧 | 必要 |

#### 3. LLM (`/llm`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/llm/models` | 利用可能モデル一覧 | 必要 |
| POST | `/llm/chat` | チャット（ストリーミング対応） | 必要 |
| POST | `/llm/embeddings` | テキスト埋め込み生成 | 必要 |
| POST | `/llm/models/pull` | モデルダウンロード | 必要 |

**リクエスト例 (Chat)**:
```json
{
  "model": "gemma2:9b",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}
```

#### 4. RAG (`/rag`)

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| POST | `/rag/query` | RAGクエリ | 必要 |
| POST | `/rag/documents` | ドキュメント追加 | 必要 |
| GET | `/rag/documents` | ドキュメント一覧 | 必要 |
| DELETE | `/rag/documents/:id` | ドキュメント削除 | 必要 |
| GET | `/rag/collections` | コレクション一覧 | 必要 |

**リクエスト例 (Query)**:
```json
{
  "query": "pgvectorとは何ですか？",
  "top_k": 5,
  "collection": "knowledge_base"
}
```

## セキュリティ

### JWT認証

- **アルゴリズム**: HS256
- **有効期限**: 1時間（アクセストークン）、7日間（リフレッシュトークン）
- **ヘッダー**: `Authorization: Bearer <token>`

### レート制限

| エンドポイント | 制限 |
|----------------|------|
| `/auth/login` | 5 req/分 |
| `/llm/chat` | 10 req/分 |
| その他 | 60 req/分 |

制限超過時のレスポンス:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 30
}
```

## エラーハンドリング

### 標準エラーレスポンス

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "username",
      "issue": "Required field missing"
    }
  }
}
```

### HTTPステータスコード

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 400 | リクエストエラー |
| 401 | 認証エラー |
| 403 | 権限エラー |
| 429 | レート制限超過 |
| 500 | サーバーエラー |

## 技術スタック

- **フレームワーク**: FastAPI 0.110+
- **認証**: PyJWT 2.8+
- **レート制限**: slowapi + Redis
- **バリデーション**: Pydantic 2.0+
- **ドキュメント**: Swagger UI (自動生成)
- **CORS**: FastAPI CORS middleware

## 環境変数

```env
# API Gateway
API_GATEWAY_PORT=8000
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
REDIS_HOST=redis
REDIS_PORT=6379

# Backend Services
POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/mydb
MONGODB_URL=mongodb://admin:admin@mongodb:27017
OLLAMA_URL=http://ollama:11434
QDRANT_URL=http://qdrant:6333
```

## 依存関係

```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
pyjwt==2.8.0
python-multipart==0.0.9
slowapi==0.1.9
redis==5.0.1
pydantic==2.6.0
pydantic-settings==2.1.0
```

## デプロイ

### Docker Compose

```yaml
api-gateway:
  build: ./apps/api-gateway
  container_name: local_api_gateway
  ports:
    - "8000:8000"
  environment:
    - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  depends_on:
    - redis
    - postgres
    - mongodb
    - ollama
    - qdrant
  restart: unless-stopped
```

## 開発ロードマップ

### Phase 1: 基本実装 ✅ (計画中)
- FastAPI基本構造
- JWT認証
- レート制限
- Swagger UI

### Phase 2: サービス統合
- PostgreSQL統合
- MongoDB統合
- Redis統合
- Qdrant統合
- Ollama統合

### Phase 3: 高度な機能
- WebSocket対応（リアルタイムチャット）
- メトリクス収集（Prometheus）
- ロギング強化
- キャッシュ戦略

---

**作成日**: 2026-03-16
**最終更新**: 2026-03-16
**バージョン**: 0.1.0
