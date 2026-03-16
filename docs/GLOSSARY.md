# 用語集 / Glossary

LocalDBKitで使用される専門用語の説明です。

---

## 📚 基本用語 / Basic Terms

### Docker関連

**Docker**
- コンテナ仮想化技術。アプリケーションとその依存関係をパッケージ化して実行
- 参考: [Docker公式サイト](https://www.docker.com/)

**Docker Compose**
- 複数のDockerコンテナを一括管理するツール
- LocalDBKitでは17のサービスを`docker-compose.yml`で管理

**コンテナ (Container)**
- 独立した実行環境。OSレベルの仮想化技術
- 例: `local_postgres`, `local_mongodb`などの各サービス

**イメージ (Image)**
- コンテナの元となるテンプレート
- 例: `postgres:16`, `mongo:7`, `redis:7-alpine`

**ボリューム (Volume)**
- データを永続化するためのストレージ
- コンテナを削除してもデータは残る

---

## 🗄️ データベース用語 / Database Terms

### データベースの種類

**RDBMS (Relational Database Management System)**
- リレーショナルデータベース管理システム
- テーブル間の関係性を定義してデータを管理
- LocalDBKitでは: PostgreSQL

**NoSQL**
- 非リレーショナルデータベース
- スキーマレス、柔軟なデータ構造
- LocalDBKitでは: MongoDB（ドキュメント型）

**KVS (Key-Value Store)**
- キー・バリュー・ストア
- シンプルなキー→値のマッピング
- 高速なキャッシュに最適
- LocalDBKitでは: Redis

**ベクトルデータベース (Vector Database)**
- 高次元ベクトルの類似度検索に特化したDB
- AI/ML、RAGシステムで活用
- LocalDBKitでは: Qdrant、PostgreSQL + pgvector

---

### PostgreSQL関連

**pgvector**
- PostgreSQLのベクトル検索拡張機能
- 埋め込みベクトル（Embeddings）を効率的に検索
- インストール: `CREATE EXTENSION vector;`

**インデックス (Index)**
- データ検索を高速化するデータ構造
- pgvectorでは: IVFFlat, HNSW

**接続文字列 (Connection String)**
```
postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
```

---

### MongoDB関連

**ドキュメント (Document)**
- MongoDBの基本データ単位（JSONライク）
- RDBMSの「行」に相当

**コレクション (Collection)**
- ドキュメントの集合
- RDBMSの「テーブル」に相当

**BSON**
- Binary JSON
- MongoDBの内部データ形式

---

### Redis関連

**キャッシュ (Cache)**
- 頻繁にアクセスされるデータを高速メモリに保存
- データベースの負荷軽減

**TTL (Time To Live)**
- データの有効期限（秒単位）
- 例: `SETEX key 3600 "value"` → 1時間後に自動削除

**パブ/サブ (Pub/Sub)**
- メッセージング機能
- Publisher（送信者）とSubscriber（受信者）

---

### Qdrant関連

**コレクション (Collection)**
- ベクトルの集合
- 各コレクションは同じ次元数のベクトルを格納

**ポイント (Point)**
- IDとベクトル、メタデータを持つデータ単位

**距離関数 (Distance Function)**
- コサイン類似度（Cosine）
- ユークリッド距離（Euclid）
- ドット積（Dot）

---

## 🤖 AI/LLM用語 / AI/LLM Terms

### LLM (Large Language Model)

**大規模言語モデル**
- 大量のテキストデータで学習したAIモデル
- 自然言語を理解・生成
- 例: GPT, Claude, Gemma, Qwen

**Ollama**
- ローカルでLLMを実行するためのツール
- LocalDBKitで使用しているLLMランタイム
- 参考: [Ollama公式サイト](https://ollama.com/)

**プロンプト (Prompt)**
- LLMへの入力テキスト（指示文）
- 出力品質はプロンプト次第

**トークン (Token)**
- LLMが処理するテキストの最小単位
- 日本語: 約1文字 = 1-2トークン
- 英語: 約1単語 = 1トークン

---

### RAG (Retrieval-Augmented Generation)

**検索拡張生成**
- 外部知識を検索してLLMに渡す技術
- LLMの幻覚（Hallucination）を軽減

**ワークフロー**:
```
1. ユーザーの質問
2. ベクトル検索で関連知識を取得
3. 知識をプロンプトに含めてLLMに送信
4. LLMが知識に基づいて回答生成
```

**マルチモーダルRAG**
- テキスト、画像、PDF、音声など複数の形式に対応
- LocalDBKit v0.3.0で実装

---

### Embeddings（埋め込みベクトル）

**ベクトル化**
- テキストを高次元の数値配列に変換
- 意味が近いテキスト → 近いベクトル

**次元数 (Dimensions)**
- ベクトルの要素数
- Gemma2:9b: 3584次元
- OpenAI text-embedding-3-small: 1536次元

**類似度検索 (Similarity Search)**
- コサイン類似度などで近いベクトルを検索
- RAGの知識取得で使用

---

### OCR (Optical Character Recognition)

**光学文字認識**
- 画像からテキストを抽出する技術
- LocalDBKitではTesseractを使用
- 対応: 日本語、英語など多言語

---

## 🔐 認証・セキュリティ / Authentication & Security

### JWT (JSON Web Token)

**認証トークン**
- サーバーレス認証に使用
- ヘッダー、ペイロード、署名の3部構成

**使い方（LocalDBKit）**:
```bash
# 1. ログイン
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin&password=admin" | jq -r '.access_token')

# 2. 認証付きリクエスト
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/llm/models
```

**有効期限**
- デフォルト: 30分
- 環境変数で変更可能

---

### CORS (Cross-Origin Resource Sharing)

**オリジン間リソース共有**
- Webブラウザのセキュリティ機能
- 異なるドメインからのAPIアクセスを制御

**LocalDBKitの設定**:
```python
# apps/api-gateway/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では制限すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### レート制限 (Rate Limiting)

**アクセス制限**
- API乱用を防ぐ
- LocalDBKit: デフォルト 100リクエスト/分

**レスポンスヘッダー**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1234567890
```

---

## 📊 監視・運用 / Monitoring & Operations

### Prometheus

**メトリクス収集システム**
- 時系列データベース
- Pull型（定期的にスクレイピング）

**メトリクスの種類**:
- Counter: 累積カウンター
- Gauge: 変動する値
- Histogram: 分布
- Summary: サマリー

---

### Grafana

**可視化ツール**
- Prometheusのデータをダッシュボード表示
- アラート機能

**LocalDBKitのダッシュボード**:
- データベースメトリクス
- LLMパフォーマンス
- APIレイテンシ

---

### ヘルスチェック (Health Check)

**サービス稼働状態の確認**
```bash
# 全サービス一括
make health

# 個別確認
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Multimodal Processor
```

---

## 🌐 API関連 / API Terms

### REST API

**HTTPベースのAPI設計スタイル**
- リソース指向
- HTTPメソッド: GET, POST, PUT, DELETE

**エンドポイント例（LocalDBKit）**:
```
GET  /api/v1/llm/models         # モデル一覧
POST /api/v1/llm/chat           # チャット
POST /api/v1/rag/query          # RAGクエリ
POST /api/v1/rag/documents      # ドキュメント追加
```

---

### 非同期処理 (Async)

**asyncio（Python）**
- 非同期I/O処理
- 高速なAPIレスポンス
- LocalDBKitではFastAPIで使用

```python
async def get_models():
    async with httpx.AsyncClient() as client:
        response = await client.get("...")
    return response.json()
```

---

### ストリーミング (Streaming)

**データを逐次送信**
- LLMの応答をリアルタイム表示
- Server-Sent Events (SSE)

```python
# Ollamaストリーミング例
{"stream": true}
```

---

## 📦 開発ツール / Development Tools

### Make

**ビルド自動化ツール**
- `Makefile`でコマンドを定義
- `make <target>`で実行

**LocalDBKitの主要コマンド**:
```bash
make up      # サービス起動
make down    # サービス停止
make health  # ヘルスチェック
make logs    # ログ表示
```

---

### Git

**バージョン管理システム**
```bash
git clone <URL>      # リポジトリ複製
git add .            # 変更をステージ
git commit -m "..."  # コミット
git push             # リモートに送信
```

---

### 環境変数 (Environment Variables)

**設定値の外部化**
- `.env`ファイルに記述
- セキュリティ向上（パスワードをコードに含めない）

**LocalDBKitの例**:
```bash
POSTGRES_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_jwt_secret_key
```

---

## 🔧 その他 / Others

### マイクロサービス (Microservices)

**小さな独立したサービスの集合**
- LocalDBKitの構成:
  - API Gateway（認証、ルーティング）
  - Multimodal Processor（OCR、PDF処理）
  - 各データベース（PostgreSQL、MongoDB、Redis、Qdrant）
  - Ollama（LLM実行）

---

### ポート (Port)

**ネットワーク通信の窓口**

**LocalDBKitのポート一覧**:
| サービス | ポート | URL |
|---------|--------|-----|
| PostgreSQL | 5432 | - |
| MongoDB | 27017 | - |
| Redis | 6379 | - |
| Qdrant | 6333 | http://localhost:6333 |
| Adminer | 8080 | http://localhost:8080 |
| Mongo Express | 8081 | http://localhost:8081 |
| Redis Commander | 8082 | http://localhost:8082 |
| Open WebUI | 3000 | http://localhost:3000 |
| Grafana | 3001 | http://localhost:3001 |
| Prometheus | 9090 | http://localhost:9090 |
| API Gateway | 8000 | http://localhost:8000 |
| Multimodal | 8001 | http://localhost:8001 |

---

## 📖 参考リンク / References

### 公式ドキュメント
- [PostgreSQL](https://www.postgresql.org/docs/)
- [MongoDB](https://docs.mongodb.com/)
- [Redis](https://redis.io/docs/)
- [Qdrant](https://qdrant.tech/documentation/)
- [Docker](https://docs.docker.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Ollama](https://ollama.com/)

### LocalDBKit関連ドキュメント
- [README.md](../README.md) - プロジェクト概要
- [QUICKSTART.md](guides/QUICKSTART.md) - クイックスタート
- [ARCHITECTURE.md](reference/ARCHITECTURE.md) - アーキテクチャ詳細
- [API_GATEWAY_GUIDE.md](guides/API_GATEWAY_GUIDE.md) - API Gateway完全ガイド

---

## 🙋 質問・フィードバック

この用語集に追加してほしい用語がある場合は、[Issues](https://github.com/HalkPapa/LocalDBKit/issues)でお知らせください！

---

**最終更新**: 2026年3月16日
**バージョン**: v0.3.0
