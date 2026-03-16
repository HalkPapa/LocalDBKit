# LocalDBKit

![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)
[![License: Timed Personal Use](https://img.shields.io/badge/License-Timed%20Personal%20Use-orange.svg)](LICENSE)
[![Future: Apache 2.0](https://img.shields.io/badge/Future-Apache%202.0-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248.svg)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg)](https://redis.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Latest-24386C.svg)](https://qdrant.tech/)
![Status](https://img.shields.io/badge/Status-Stable-green.svg)

🗄️ Complete local database development kit with Docker Compose

ローカル開発用のオールインワンデータベース環境です。PostgreSQL、MongoDB、Redis、Qdrantに加え、Ollama LLMとRAGシステムを統合しています。

[English README](README_EN.md)

---

## ⚠️ Production Readiness / 本番環境対応状況

**Current Status: Stable for Local Development / ローカル開発向け安定版 (v1.0.0)**

LocalDBKit is currently suitable for:
- ✅ **Local development environments** - 完全にローカルで動作
- ✅ **Learning and experimentation** - AI/RAG技術の学習に最適
- ✅ **Proof-of-concept projects** - アイデア検証・プロトタイピング

**NOT recommended for production use** without addressing:
- 🔴 **Authentication system** - Hardcoded test users (`admin:admin`)
- 🔴 **Token management** - JWT tokens cannot be invalidated after logout
- 🔴 **Performance optimizations** - No caching, batching, or connection pooling
- 🔴 **Role-based access control** - No RBAC implementation

**本番環境での使用には以下の改善が必要です**:
- 認証システムの本格実装（PostgreSQL/MongoDBベースのユーザー管理）
- トークン無効化機構（Redisブラックリスト）
- パフォーマンス最適化（キャッシュ、バッチ処理、コネクションプーリング）
- ロールベースアクセス制御（RBAC）

📋 詳細な改善計画は [ROADMAP.md](ROADMAP.md) を参照してください。

---

## ⚡ クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/HalkPapa/LocalDBKit.git
cd LocalDBKit

# 2. 環境変数設定
cp .env.example .env
# ⚠️ IMPORTANT: Edit .env and change all passwords before production use!
# 重要: .envファイルを編集し、本番環境では必ず全パスワードを変更してください！

# 3. 全サービス起動
make up

# 4. ヘルスチェック
make health

# 5. Open WebUIにアクセス
open http://localhost:3000
```

### 📋 主要コマンド

| コマンド | 説明 |
|---------|------|
| `make up` | 全サービス起動 |
| `make down` | 全サービス停止 |
| `make health` | ヘルスチェック |
| `make backup` | データバックアップ |
| `make logs` | ログ表示 |
| `make help` | 全コマンド表示 |

詳細は `make help` を実行してください。

## 📖 ドキュメント

**全ドキュメントは [docs/](docs/) フォルダに整理されています。**

### 🚀 クイックスタート
- **[QUICKSTART.md](docs/guides/QUICKSTART.md)** - 5分で始めるクイックスタート
- **[GLOSSARY.md](docs/GLOSSARY.md)** - 用語集（RAG、JWT、Embeddingなど専門用語の説明）

### 📖 ガイド
- **[SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md)** - 完全なセットアップガイド（初めての方はこちら）
- **[DOCKER_GUIDE.md](docs/guides/DOCKER_GUIDE.md)** - Docker完全ガイド（全てDockerで動作）
- **[FLOW_GUIDE.md](docs/guides/FLOW_GUIDE.md)** - システム使用フロー完全ガイド
- **[API_GATEWAY_GUIDE.md](docs/guides/API_GATEWAY_GUIDE.md)** - API Gateway完全ガイド（NEW! v0.3.0）
- **[LLM_GUIDE.md](docs/guides/LLM_GUIDE.md)** - ローカルLLMシステムガイド
- **[MULTI_APP_GUIDE.md](docs/guides/MULTI_APP_GUIDE.md)** - 複数アプリ・ゲーム管理ガイド
- **[BACKUP_GUIDE.md](docs/guides/BACKUP_GUIDE.md)** - バックアップ・リストア完全ガイド（v0.2.0）

### 📋 リファレンス
- **[ARCHITECTURE.md](docs/reference/ARCHITECTURE.md)** - システムアーキテクチャ詳細（NEW!）
- **[DATABASES.md](docs/reference/DATABASES.md)** - 各データベースの比較と使い分けガイド
- **[APP_DATABASE_MAP.md](docs/reference/APP_DATABASE_MAP.md)** - アプリ・DBマッピング（1ファイル完結）

### 🎨 図・ダイアグラム
- **[architecture.drawio](docs/diagrams/architecture.drawio)** - アーキテクチャ図（編集可能）（NEW!）
- **[flow.drawio](docs/diagrams/flow.drawio)** - 使用フロー図（編集可能）（NEW!）

### 📝 プロジェクト情報
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - プロジェクトサマリー（エージェント向け）
- **[WORK_LOG.md](docs/WORK_LOG.md)** - 作業ログ（構築の全記録）
- **[ROADMAP.md](ROADMAP.md)** - 開発ロードマップ（将来の計画）
- **[SCREENSHOTS.md](docs/SCREENSHOTS.md)** - UIスクリーンショット一覧（NEW! v0.2.0）

**📚 詳細は [docs/README.md](docs/README.md) を参照してください。**

## 📁 プロジェクト構造

```
LocalDBKit/
├── 📄 docker-compose.yml       # Docker構成
├── 📄 requirements.txt         # Python依存関係
│
├── 🚀 apps/                    # アプリケーション
│   ├── rag/                   # RAGシステム
│   ├── learning/              # 学習管理
│   └── dashboard/             # ダッシュボード
│
├── 🔧 scripts/                 # スクリプト
│   ├── deployment/            # デプロイメント
│   ├── knowledge/             # 知識管理
│   └── multi_app/             # マルチアプリ管理
│
├── 💾 data/                    # データ
│   ├── knowledge/             # RAG用知識
│   └── init-scripts/          # DB初期化
│
├── 📚 docs/                    # ドキュメント
│   ├── guides/                # ガイド
│   ├── reference/             # リファレンス
│   └── diagrams/              # 図・ダイアグラム
│
└── 📝 examples/                # サンプルコード
```

## 🚀 API Gateway & Multimodal RAG（NEW! v0.3.0）

統合APIとマルチモーダルRAGシステムを追加しました！

### できること
- **API Gateway**: JWT認証、レート制限、Swagger UIによる統一API
- **マルチモーダル処理**: OCR（画像）、PDF、音声、動画処理
- **マルチモーダルRAG**: テキスト・画像・PDFを横断した質問応答
- **LLM統合**: Ollama経由での埋め込み生成とLLM応答

### クイックスタート
```bash
# サービス起動
make up

# API Gateway（Swagger UI）
open http://localhost:8000/api/v1/docs

# マルチモーダルプロセッサー（Swagger UI）
open http://localhost:8001/api/v1/docs

# サンプル実行
python examples/multimodal-rag/multimodal_rag_example.py
```

詳細は **[API_GATEWAY_GUIDE.md](docs/guides/API_GATEWAY_GUIDE.md)** を参照

## 🤖 ローカルLLMシステム

完全無料・プライベートなAIチャットシステム！

### できること
- **チャットボット**: Ollamaとの会話（会話履歴保存）
- **RAG**: 自分のドキュメントを学習させて質問応答
- **セマンティック検索**: 自然言語でドキュメント検索

### クイックスタート
```bash
# LLMシステム起動
./scripts/deployment/start_llm.sh

# チャットアプリ
streamlit run apps/rag/chat_app.py

# RAGアプリ
streamlit run apps/rag/rag_app.py

# ブラウザで http://localhost:8501 を開く
```

詳細は **[LLM_GUIDE.md](docs/guides/LLM_GUIDE.md)** を参照

## 含まれるデータベース

### 1. PostgreSQL + pgvector
- **ポート**: 5432
- **用途**: リレーショナルデータベース、ベクトル検索
- **管理UI**: Adminer (http://localhost:8080)
- **拡張機能**: pgvector (ベクトル類似度検索)

### 2. Redis
- **ポート**: 6379
- **用途**: キャッシュ、セッション管理、キューイング、Pub/Sub
- **管理UI**: Redis Commander (http://localhost:8082)

### 3. MongoDB
- **ポート**: 27017
- **用途**: ドキュメント指向データベース、JSON形式データ
- **管理UI**: Mongo Express (http://localhost:8081)

### 4. Qdrant
- **ポート**: 6333 (REST API), 6334 (gRPC)
- **用途**: 専用ベクトルデータベース、セマンティック検索
- **ダッシュボード**: http://localhost:6333/dashboard

### 5. Ollama（LLMシステム）
- **ポート**: 11434
- **用途**: ローカルLLM実行環境
- **WebUI**: Streamlit (http://localhost:8501)
- **特徴**: 完全無料、プライバシー保護、オフライン動作

### 6. API Gateway（NEW! v0.3.0）
- **ポート**: 8000
- **用途**: 統合APIエンドポイント、JWT認証、レート制限
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **機能**: LLM管理、RAG、データベース統合

### 7. Multimodal Processor（NEW! v0.3.0）
- **ポート**: 8001
- **用途**: OCR、PDF処理、音声・動画処理（計画中）
- **Swagger UI**: http://localhost:8001/api/v1/docs
- **機能**: 画像からテキスト抽出、PDF解析

## 📊 モニタリング・管理（NEW! v0.2.0）

### Prometheus + Grafana監視システム

リアルタイムでデータベースのパフォーマンスを監視できます！

#### Grafanaダッシュボード
- **URL**: http://localhost:3001
- **ログイン**: admin / admin
- **機能**:
  - PostgreSQL、MongoDB、Redisのメトリクス
  - リアルタイムパフォーマンス監視
  - リソース使用状況グラフ
  - クエリ実行時間分析

#### Prometheusメトリクス
- **URL**: http://localhost:9090
- **機能**:
  - メトリクス収集エンジン
  - 時系列データストレージ
  - クエリ言語（PromQL）

詳細は **[SCREENSHOTS.md](docs/SCREENSHOTS.md)** を参照

### 自動バックアップシステム

データの安全性を保証する自動バックアップ機能を搭載しています。

#### 手動バックアップ
```bash
# バックアップ実行
make backup

# リストア実行
make restore BACKUP=./backups/20260315_120000
```

#### 自動バックアップ（cron設定）
```bash
# crontab編集
crontab -e

# 毎日午前2時に自動バックアップ
0 2 * * * /path/to/LocalDBKit/scripts/deployment/auto-backup.sh
```

**バックアップ内容**:
- PostgreSQL全データ（SQL）
- MongoDB全データ（圧縮）
- Redisスナップショット
- Qdrant全データ

詳細は **[BACKUP_GUIDE.md](docs/guides/BACKUP_GUIDE.md)** を参照

## セットアップ

### 前提条件

以下のいずれかのDocker環境が必要です：

#### オプション1: Docker Desktop（公式）
```bash
# Homebrewでインストール（管理者パスワードが必要）
brew install --cask docker

# または公式サイトからダウンロード
# https://www.docker.com/products/docker-desktop/
```

インストール後、アプリケーションフォルダから「Docker.app」を起動してください。

#### オプション2: Colima（軽量・推奨）
```bash
# Homebrewでインストール
brew install colima docker docker-compose

# Colimaを起動
colima start

# 起動確認
docker ps
```

**推奨理由**: Colimaは軽量で、管理者権限不要、メモリ使用量も少ないです。

### 初回起動手順

#### 1. Docker環境の起動

**Docker Desktopの場合:**
```bash
# アプリケーションを起動（GUIから、またはコマンドで）
open -a Docker
```

**Colimaの場合:**
```bash
colima start
```

#### 2. データベースコンテナの起動

```bash
# このディレクトリに移動
cd /path/to/データベース構築

# 全てのデータベースを起動
docker-compose up -d

# 起動状態を確認
docker ps

# またはヘルスチェックスクリプトを使用
./scripts/deployment/health-check.sh
```

**初回起動時の注意:**
- イメージのダウンロードに数分かかります（約2GB）
- 起動完了まで30秒〜1分程度待ちます

#### 3. 起動確認

ブラウザで以下の管理UIにアクセス:
- **Adminer (PostgreSQL)**: http://localhost:8080
- **Mongo Express (MongoDB)**: http://localhost:8081
- **Redis Commander (Redis)**: http://localhost:8082
- **Qdrant Dashboard**: http://localhost:6333/dashboard

または、サンプルコードを実行:
```bash
# Python依存関係をインストール
pip install -r requirements.txt

# PostgreSQLの動作確認
python examples/postgres/python_example.py
```

### 日常的な起動・停止

```bash
# 起動（2回目以降は数秒で起動）
docker-compose up -d

# 停止
docker-compose down

# ログを確認
docker-compose logs -f

# 特定のサービスのみ起動
docker-compose up -d postgres redis
```

### 停止方法

```bash
# 全てのサービスを停止
docker-compose down

# データも削除する場合
docker-compose down -v
```

### サービスの状態確認

```bash
docker-compose ps
```

## 接続情報

### PostgreSQL
```
Host: localhost
Port: 5432
User: postgres
Password: postgres
Database: mydb
```

接続文字列:
```
postgresql://postgres:postgres@localhost:5432/mydb
```

### Redis
```
Host: localhost
Port: 6379
```

接続文字列:
```
redis://localhost:6379
```

### MongoDB
```
Host: localhost
Port: 27017
User: admin
Password: admin
Database: mydb
Auth DB: admin
```

接続文字列:
```
mongodb://admin:admin@localhost:27017/mydb?authSource=admin
```

### Qdrant
```
REST API: http://localhost:6333
gRPC API: localhost:6334
Dashboard: http://localhost:6333/dashboard
```

## 管理ツール（WebベースGUI）

全てのデータベースをブラウザから操作できます！

### 1. Adminer (PostgreSQL管理)
- **URL**: http://localhost:8080
- PostgreSQLのテーブル、データ、インデックス管理
- SQL実行、エクスポート/インポート

### 2. Mongo Express (MongoDB管理)
- **URL**: http://localhost:8081
- MongoDBのドキュメント閲覧・編集・削除
- コレクション管理、インデックス管理
- JSONビューアー

### 3. Redis Commander (Redis管理)
- **URL**: http://localhost:8082
- Redisのキー・値の閲覧・編集・削除
- リアルタイムモニタリング
- TTL管理

### 4. Qdrant Dashboard (ベクトルDB管理)
- **URL**: http://localhost:6333/dashboard
- ベクトルコレクションの管理と検索
- リアルタイム類似検索テスト

## 使用例

各データベースの使用例は `examples/` ディレクトリを参照してください。

### マルチモーダルRAG例（NEW! v0.3.0）

```bash
# テキストRAG
python examples/multimodal-rag/text_rag_example.py

# マルチモーダルRAG（テキスト + 画像）
python examples/multimodal-rag/multimodal_rag_example.py
```

詳細は [examples/multimodal-rag/README.md](examples/multimodal-rag/README.md) を参照

## データの永続化

全てのデータは Docker volumes に保存されます：
- `postgres_data` - PostgreSQLデータ
- `redis_data` - Redisデータ
- `mongodb_data` - MongoDBデータ
- `qdrant_data` - Qdrantデータ

## トラブルシューティング

### Docker デーモンが起動していない

**エラー**: `Cannot connect to the Docker daemon`

**解決方法:**

Docker Desktopの場合:
```bash
# Docker.appを起動
open -a Docker

# 起動を待つ（30秒〜1分）
sleep 30
docker ps
```

Colimaの場合:
```bash
# Colimaを起動
colima start

# 状態確認
colima status
```

### コンテナが表示されない

**症状**: `docker ps` でコンテナが表示されない

**解決方法:**
```bash
# 現在のディレクトリを確認
pwd

# docker-compose.yml があるディレクトリで実行
cd /path/to/データベース構築
docker-compose up -d

# コンテナを確認
docker ps
```

### ポートが既に使用されている

**エラー**: `Bind for 0.0.0.0:5432 failed: port is already allocated`

**解決方法:**
```bash
# 使用中のポートを確認
lsof -i :5432
lsof -i :6379
lsof -i :27017
lsof -i :6333

# 使用中のプロセスを停止するか、
# docker-compose.yml のポートを変更してください
# 例: "15432:5432" (ホスト側のみ変更)
```

### データベースに接続できない

**症状**: サンプルコードで `Connection refused` エラー

**解決方法:**
```bash
# 1. コンテナが起動しているか確認
docker ps

# 2. ヘルスチェック実行
./scripts/deployment/health-check.sh

# 3. ログを確認
docker-compose logs postgres
docker-compose logs redis
docker-compose logs mongodb
docker-compose logs qdrant

# 4. コンテナを再起動
docker-compose restart
```

### データをリセットしたい

**完全リセット:**
```bash
# コンテナとデータを全て削除
docker-compose down -v

# 再起動
docker-compose up -d
```

**特定のデータベースのみリセット:**
```bash
# PostgreSQLのみ
docker-compose stop postgres
docker volume rm local_databases_postgres_data
docker-compose up -d postgres
```

### サービスが起動しない

**ログ確認:**
```bash
# 全サービスのログ
docker-compose logs

# 特定のサービスのログ
docker-compose logs postgres
docker-compose logs redis
docker-compose logs mongodb
docker-compose logs qdrant

# リアルタイムでログを監視
docker-compose logs -f
```

**完全再構築:**
```bash
# 全て削除して再構築
docker-compose down -v
docker-compose up -d --force-recreate
```

### Colima が起動しない

**エラー**: `colima start` でエラーが発生

**解決方法:**
```bash
# Colimaを完全停止
colima stop

# 設定を削除して再作成
colima delete
colima start

# CPUとメモリを指定して起動
colima start --cpu 4 --memory 8
```

### イメージのダウンロードが遅い

**対処法:**
```bash
# 個別にイメージを事前ダウンロード
docker pull ankane/pgvector:latest
docker pull redis:7-alpine
docker pull mongo:7
docker pull qdrant/qdrant:latest
docker pull adminer:latest

# その後起動
docker-compose up -d
```

## セキュリティ注意事項

これは**開発環境専用**です。本番環境では：
- 強力なパスワードを設定
- ネットワークを適切に分離
- SSL/TLS接続を有効化
- 定期的なバックアップを実施

---

## 📜 ライセンス / License

**LocalDBKit Timed Personal Use License**

このソフトウェアは**期限付き個人利用ライセンス**の下で提供されています。

### ⏰ ライセンスタイムライン

```
2026年〜2029年3月15日: Timed Personal Use License
        ↓
2029年3月16日〜: Apache License 2.0（自動変換）
```

### ✅ 現在（2029年3月15日まで）許可されていること

**個人利用**
- 個人的な非商用利用
- 学習・研究目的での使用

**小規模商用利用**（以下のいずれかを満たす場合）
- 従業員10人未満の組織
- 年間売上1億円未満の組織

**教育・研究利用**
- 学校・大学での使用
- 学術研究機関での使用

**その他**
- ソースコードの閲覧・改変（内部利用のみ）
- バグ報告・プルリクエストでの貢献
- 評価・テスト目的（90日間）

### ❌ 禁止されていること

**改変版の配布**（重要！）
- 改変したコードの公開・配布
- マルウェア混入や評判毀損を防ぐため

**大規模商用利用**
- 従業員10人以上 AND 年間売上1億円以上の組織
- → 商用ライセンスが必要です

### 🎉 2029年3月16日以降（自動的にオープンソース化）

Apache License 2.0 に自動変換され、以下が可能になります:
- ✅ 制限なしの商用利用
- ✅ 改変版の配布
- ✅ プロプライエタリソフトウェアでの使用

### 💰 商用ライセンスについて

大規模組織（従業員10人以上 AND 売上1億円以上）で商用利用をご希望の場合は、
お問い合わせください:

**連絡先**: https://github.com/HalkPapa

**参考料金**（年間・交渉可能）:
- 10-50人規模: $2,000 - $5,000
- 51-200人規模: $5,000 - $15,000
- 201人以上: 個別相談

### ⚠️ セキュリティ警告

**公式リポジトリからのみダウンロードしてください**:
https://github.com/HalkPapa/LocalDBKit

改変版や非公式版にはマルウェアが含まれる可能性があります。

詳細は [LICENSE](LICENSE) ファイルをご確認ください。

---

## 💖 サポート / Support

このプロジェクトが役に立った場合は、ぜひサポートをご検討ください！

### カンパ・寄付 / Donations
開発継続のためのカンパ・寄付を大歓迎します。

**寄付方法**:
- GitHub Sponsors: [HalkPapa](https://github.com/sponsors/HalkPapa)（準備中）
- その他の方法については [FUNDING.yml](.github/FUNDING.yml) をご確認ください

### その他の貢献方法
- ⭐ GitHubでスター
- 🐛 バグレポート
- 💡 機能提案
- 📖 ドキュメント改善
- 🌐 翻訳協力

---

## 🙏 謝辞 / Acknowledgments

このプロジェクトは以下のオープンソースプロジェクトに支えられています：
- [PostgreSQL](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector)
- [MongoDB](https://www.mongodb.com/)
- [Redis](https://redis.io/)
- [Qdrant](https://qdrant.tech/)
- [Ollama](https://ollama.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/)

---

**© 2026 HalkPapa. All rights reserved.**
