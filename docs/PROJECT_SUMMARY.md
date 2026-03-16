# プロジェクトサマリー

このドキュメントは、他のAIエージェントやチームメンバーがプロジェクトを即座に理解できるように、全体像をまとめたものです。

---

## 🎯 プロジェクト概要

**目的**: ローカル開発環境で使える、複数のデータベースを統合した開発環境の構築

**構成**: Docker Composeで管理された4種類のデータベースと3つの管理UIツール

**対象ユーザー**:
- ローカル開発でデータベースを使いたい開発者
- 複数のDBを学習・実験したい人
- Supabaseのようなローカル環境を構築したい人

**開発環境**: macOS (Apple Silicon / M1/M2)、Docker (Colima推奨)

---

## 📦 含まれるコンポーネント

### データベース (4種類)

1. **PostgreSQL + pgvector** (ポート: 5432)
   - リレーショナルデータベース
   - ベクトル検索機能付き (pgvector拡張)
   - 用途: SQL、ベクトル類似検索

2. **MongoDB** (ポート: 27017)
   - ドキュメント指向NoSQLデータベース
   - 用途: JSON形式データ、柔軟なスキーマ

3. **Redis** (ポート: 6379)
   - インメモリKVS
   - 用途: キャッシュ、セッション管理、キューイング、Pub/Sub

4. **Qdrant** (ポート: 6333, 6334)
   - ベクトル専用データベース
   - 用途: セマンティック検索、ベクトル類似検索

### 管理ツール (3種類)

1. **Adminer** (ポート: 8080)
   - PostgreSQL管理UI
   - SQL実行、テーブル管理

2. **Mongo Express** (ポート: 8081)
   - MongoDB管理UI
   - ドキュメント閲覧・編集、コレクション管理

3. **Qdrant Dashboard** (ポート: 6333/dashboard)
   - Qdrant公式管理UI
   - ベクトル検索テスト

**注意**: Redis Commander (ポート: 8082) は含まれていますが、M1/M2 Macとの互換性問題で動作していません。

---

## 🏗️ アーキテクチャ

### システム構成図

```
┌─────────────────────────────────────────┐
│        Docker Compose 環境              │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │PostgreSQL│  │ MongoDB │  │  Redis  ││
│  │+ pgvector│  │         │  │         ││
│  └────┬────┘  └────┬────┘  └────┬────┘│
│       │            │             │     │
│       └────────────┴─────────────┘     │
│                                         │
│  ┌─────────┐  ┌──────────────────┐    │
│  │ Qdrant  │  │   管理ツール     │    │
│  │         │  │  - Adminer       │    │
│  └─────────┘  │  - Mongo Express │    │
│               │  - Qdrant UI     │    │
│               └──────────────────┘    │
└─────────────────────────────────────────┘
         │
         │ Docker Volumes (データ永続化)
         ▼
┌─────────────────────────────────────────┐
│ postgres_data, mongodb_data, redis_data │
│ qdrant_data, mongodb_config             │
└─────────────────────────────────────────┘
```

### Docker構成

- **Dockerイメージ**: 公式イメージを使用（ankane/pgvector, mongo:7, redis:7-alpine, qdrant/qdrant, adminer, mongo-express）
- **ネットワーク**: 全コンテナが同一Dockerネットワーク内で通信
- **データ永続化**: Docker Volumesで各DBのデータを永続化
- **管理**: docker-compose.yml で一元管理

---

## 📁 ファイル構成

```
データベース構築/
├── README.md                   # プロジェクト概要・詳細リファレンス
├── PROJECT_SUMMARY.md          # このファイル（エージェント向けサマリー）
├── SETUP_GUIDE.md              # 初回セットアップ手順（詳細版）
├── QUICKSTART.md               # 5分で始めるクイックスタート
├── DOCKER_GUIDE.md             # Docker完全ガイド（操作・管理）
├── DATABASES.md                # 各DBの比較・使い分けガイド
│
├── docker-compose.yml          # ★重要★ Docker構成定義
├── .env                        # ★重要★ 環境変数・接続情報
├── .env.example                # 環境変数のテンプレート
│
├── start.sh                    # 起動スクリプト（自動環境チェック付き）
├── scripts/deployment/health-check.sh             # ヘルスチェックスクリプト
│
├── init-scripts/               # PostgreSQL初期化スクリプト
│   └── 01-init.sql             # pgvector拡張、サンプルテーブル作成
│
├── examples/                   # サンプルコード（全DB対応）
│   ├── postgres/
│   │   ├── python_example.py   # PostgreSQL + pgvector例
│   │   └── nodejs_example.js   # Node.js例
│   ├── mongodb/
│   │   └── python_example.py   # MongoDB CRUD例
│   ├── redis/
│   │   └── python_example.py   # Redis全機能例
│   └── qdrant/
│       └── python_example.py   # Qdrant ベクトル検索例
│
├── requirements.txt            # Python依存関係
└── package.json                # Node.js依存関係
```

---

## 🔧 技術スタック

### インフラ
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナ管理
- **Colima**: 軽量Docker環境 (Docker Desktopの代替、推奨)

### データベース
- **PostgreSQL 16** + **pgvector**: RDB、ベクトル検索
- **MongoDB 7**: NoSQL、ドキュメントDB
- **Redis 7**: KVS、キャッシュ
- **Qdrant**: ベクトル専用DB

### 管理ツール
- **Adminer**: PostgreSQL管理UI
- **Mongo Express**: MongoDB管理UI
- **Qdrant Dashboard**: Qdrant公式UI

### プログラミング言語
- **Python 3.x**: 主要なサンプルコード
- **Node.js**: PostgreSQL例のみ

---

## ⚙️ 重要な設定

### 接続情報

#### PostgreSQL
```
Host: localhost
Port: 5432
User: postgres
Password: postgres
Database: mydb
接続文字列: postgresql://postgres:postgres@localhost:5432/mydb
```

#### MongoDB
```
Host: localhost
Port: 27017
User: admin
Password: admin
Database: mydb
Auth DB: admin
接続文字列: mongodb://admin:admin@localhost:27017/mydb?authSource=admin
```

#### Redis
```
Host: localhost
Port: 6379
接続文字列: redis://localhost:6379
```

#### Qdrant
```
REST API: http://localhost:6333
gRPC API: localhost:6334
Dashboard: http://localhost:6333/dashboard
```

### 環境変数 (.env)

```bash
# データベース接続
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://admin:admin@localhost:27017/mydb?authSource=admin
QDRANT_URL=http://localhost:6333

# Docker Compose設定
COMPOSE_PROJECT_NAME=local_databases  # ★重要★ 日本語ディレクトリ対策
```

### Docker設定

**Colima使用時の必須設定:**
```bash
# ~/.zshrc または ~/.bashrc に追加
export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock
```

**Colimaリソース設定:**
```bash
colima start --disk 60 --cpu 4 --memory 8
```

---

## 🚀 基本操作

### 起動

```bash
# プロジェクトディレクトリに移動
cd /path/to/LocalDBKit

# 全サービス起動
docker-compose up -d

# または起動スクリプト使用
./start.sh
```

### 確認

```bash
# コンテナ状態確認
docker-compose ps

# ヘルスチェック
./scripts/deployment/health-check.sh
```

### 停止

```bash
# 全サービス停止
docker-compose down

# データも削除（注意！）
docker-compose down -v
```

### 管理UIアクセス

- Adminer: http://localhost:8080
- Mongo Express: http://localhost:8081
- Qdrant Dashboard: http://localhost:6333/dashboard

---

## 🐛 よくある問題と解決方法

### 1. Docker デーモンが起動していない

**エラー**: `Cannot connect to the Docker daemon`

**原因**: Docker/Colimaが起動していない

**解決**:
```bash
# Colimaの場合
colima start

# Docker Desktopの場合
open -a Docker
```

### 2. ディスク容量不足

**エラー**: `no space left on device`

**原因**: Mac本体またはColimaのディスクが一杯

**解決**:
```bash
# Colimaを削除して大きなディスクで再作成
colima delete
colima start --disk 60 --cpu 4 --memory 8

# 不要なDockerリソース削除
docker system prune -a --volumes
```

### 3. COMPOSE_PROJECT_NAME が空

**エラー**: `project name must not be empty`

**原因**: ディレクトリ名に日本語が含まれている

**解決**: `.env` に以下を追加（既に設定済み）
```bash
COMPOSE_PROJECT_NAME=local_databases
```

### 4. PostgreSQL JSONB型エラー

**エラー**: `can't adapt type 'dict'`

**原因**: PythonのdictをそのままJSONBに挿入できない

**解決**: `psycopg2.extras.Json()` でラップ
```python
from psycopg2.extras import Json
cur.execute("INSERT ... VALUES (%s)", (Json({"key": "value"}),))
```

### 5. Qdrant API エラー

**エラー**: `'QdrantClient' object has no attribute 'search'`

**原因**: Qdrant APIが変更された

**解決**: 新しいAPIメソッドを使用（既に修正済み）
```python
# 旧API
client.search(...)

# 新API
client.query_points(...).points
```

### 6. Redis Commander が起動しない

**エラー**: コンテナがRestartingを繰り返す

**原因**: M1/M2 Macとの互換性問題

**解決**: CLIまたはPythonコードで操作
```bash
docker exec local_redis redis-cli
```

---

## 📝 開発の経緯・解決した問題

### 構築フェーズ1: 基本環境構築
1. Docker Composeで4つのデータベースを構築
2. 各データベースの初期化スクリプト作成
3. サンプルコード作成（Python中心）

### 構築フェーズ2: GUI追加
1. Adminer、Mongo Express追加
2. Redis Commander追加（後に互換性問題が判明）
3. 統合管理ツールの検討→既存ツールで十分と判断

### 問題解決フェーズ
1. **日本語ディレクトリ問題**: COMPOSE_PROJECT_NAME追加で解決
2. **DOCKER_HOST問題**: Colima使用時の環境変数設定で解決
3. **PostgreSQL JSONB問題**: Json()ラッパーで解決
4. **Qdrant API変更**: 新APIメソッドに書き換え
5. **ディスク容量不足**: Colimaディスクサイズ拡大、クリーンアップ
6. **Redis Commander互換性**: 解決せず（CLI使用で代替）

### ドキュメント整備
1. README.md - 全体概要
2. SETUP_GUIDE.md - 初心者向けセットアップ
3. QUICKSTART.md - 5分で始める
4. DOCKER_GUIDE.md - Docker操作完全版
5. PROJECT_SUMMARY.md - このファイル

---

## 🎓 学んだこと・ベストプラクティス

### Docker構成
- ✅ docker-compose.ymlで全サービスを一元管理
- ✅ Docker Volumesでデータ永続化
- ✅ ヘルスチェックで各サービスの状態監視
- ✅ depends_onで起動順序制御

### ポート管理
- ✅ 標準ポートをそのまま使用（変更不要）
- ✅ 管理UIは8080番台に集約
- ✅ コンテナ間通信はサービス名で可能

### データベース管理
- ✅ 各DBに専用の管理UIを用意
- ✅ サンプルコードで動作確認
- ✅ 初期化スクリプトで環境構築自動化

### ドキュメント
- ✅ 用途別に複数のドキュメント作成
- ✅ トラブルシューティングを充実
- ✅ エージェント向けサマリー作成

---

## 🔮 今後の拡張案

### 追加可能なDB
- Elasticsearch (全文検索)
- Neo4j (グラフDB)
- Cassandra (分散DB)

### 機能拡張
- バックアップ自動化スクリプト
- モニタリングツール追加 (Grafana, Prometheus)
- CI/CD統合
- 本番環境用設定（セキュリティ強化版）

### 管理ツール
- CloudBeaver追加（PostgreSQL + MongoDB統合管理）
- RedisInsight（Redis公式GUI、M1/M2対応版）
- 簡易統合ダッシュボード（Streamlit製）

---

## 🎯 エージェント向け推奨読了順

このプロジェクトを理解するための推奨読了順:

### 最小限（5分）
1. **PROJECT_SUMMARY.md** （このファイル）
2. **docker-compose.yml** （実際の構成）

### 基本理解（15分）
1. PROJECT_SUMMARY.md
2. README.md
3. docker-compose.yml
4. DOCKER_GUIDE.md

### 完全理解（30分）
1. 上記全て
2. SETUP_GUIDE.md
3. DATABASES.md
4. examples/*/python_example.py

---

## 📊 プロジェクト統計

- **Dockerコンテナ**: 7個
- **データベース**: 4種類
- **管理UI**: 3個（4個目は互換性問題）
- **ドキュメント**: 6ファイル
- **サンプルコード**: 5ファイル
- **対応言語**: Python, Node.js
- **総コード行数**: 約2000行
- **開発時間**: 約3-4時間

---

## ✅ チェックリスト

他のエージェントがこのプロジェクトを引き継ぐ際の確認事項:

- [ ] Docker/Colimaが起動しているか確認
- [ ] DOCKER_HOST環境変数が設定されているか
- [ ] docker-compose ps で全コンテナがUpか確認
- [ ] 管理UIにアクセスできるか
- [ ] サンプルコードが実行できるか
- [ ] ドキュメントを読んで全体像を把握

---

## 📞 サポート情報

### ドキュメント
- README.md - 詳細なリファレンス
- DOCKER_GUIDE.md - Docker操作方法
- SETUP_GUIDE.md - セットアップ手順

### サンプルコード
- examples/ - 全DB対応のPython例

### トラブルシューティング
- このファイルの「よくある問題」セクション参照
- README.md のトラブルシューティングセクション参照

---

**最終更新**: 2026年3月9日
**プロジェクトステータス**: ✅ 完成・稼働中
**メンテナンス**: 不要（安定動作中）
