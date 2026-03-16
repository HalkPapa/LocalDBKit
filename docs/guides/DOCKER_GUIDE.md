# Docker 完全ガイド

このプロジェクトは**全てDockerで動作**しています。複数のデータベースとツールがDockerコンテナとして起動します。

---

## 📦 構成

### Dockerコンテナ一覧

現在、以下の**7つのコンテナ**が docker-compose で管理されています:

| コンテナ名 | 役割 | ポート | イメージ |
|-----------|------|--------|----------|
| local_postgres | PostgreSQL + pgvector | 5432 | ankane/pgvector:latest |
| local_redis | Redis | 6379 | redis:7-alpine |
| local_mongodb | MongoDB | 27017 | mongo:7 |
| local_qdrant | Qdrant | 6333, 6334 | qdrant/qdrant:latest |
| local_adminer | Adminer (PostgreSQL管理UI) | 8080 | adminer:latest |
| local_mongo_express | Mongo Express (MongoDB管理UI) | 8081 | mongo-express:latest |
| local_redis_commander | Redis Commander (Redis管理UI) | 8082 | rediscommander/redis-commander:latest |

### データ永続化（Docker Volumes）

以下のDocker volumesでデータが永続化されています:

```
postgres_data    → PostgreSQLのデータ
redis_data       → Redisのデータ
mongodb_data     → MongoDBのデータ
mongodb_config   → MongoDBの設定
qdrant_data      → Qdrantのデータ
```

---

## 🚀 基本操作

### 全サービス起動

```bash
# プロジェクトディレクトリに移動
cd /path/to/LocalDBKit

# 全コンテナを起動（バックグラウンド）
docker-compose up -d
```

**初回起動**: イメージダウンロードに1-2分
**2回目以降**: 5-10秒で起動

### 起動確認

```bash
# 起動中のコンテナを確認
docker-compose ps

# または
docker ps
```

**期待される出力:**
```
NAME                      STATUS
local_postgres           Up (healthy)
local_redis              Up (healthy)
local_mongodb            Up (healthy)
local_qdrant             Up (healthy)
local_adminer            Up
local_mongo_express      Up
local_redis_commander    Up または Restarting
```

### 全サービス停止

```bash
# 全コンテナを停止
docker-compose down

# データも削除する場合（注意！）
docker-compose down -v
```

### ログ確認

```bash
# 全サービスのログ
docker-compose logs

# リアルタイムでログ監視
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs redis
docker-compose logs qdrant
```

---

## 🔧 個別サービス操作

### 特定サービスのみ起動

```bash
# PostgreSQLとRedisのみ起動
docker-compose up -d postgres redis

# MongoDBのみ起動
docker-compose up -d mongodb
```

### 特定サービスの再起動

```bash
# PostgreSQLのみ再起動
docker-compose restart postgres

# 全サービス再起動
docker-compose restart
```

### 特定サービスの停止

```bash
# Qdrantのみ停止
docker-compose stop qdrant

# 停止したサービスを再開
docker-compose start qdrant
```

---

## 🗄️ データ管理

### データのバックアップ

#### PostgreSQLのバックアップ

```bash
# データベース全体をバックアップ
docker exec local_postgres pg_dump -U postgres mydb > backup_postgres.sql

# 特定のテーブルのみ
docker exec local_postgres pg_dump -U postgres -t users mydb > backup_users.sql
```

#### MongoDBのバックアップ

```bash
# データベース全体をバックアップ
docker exec local_mongodb mongodump --username admin --password admin --authenticationDatabase admin --out /tmp/backup

# バックアップをホストにコピー
docker cp local_mongodb:/tmp/backup ./backup_mongodb
```

#### Redisのバックアップ

```bash
# RDBファイルを保存
docker exec local_redis redis-cli SAVE

# バックアップファイルをコピー
docker cp local_redis:/data/dump.rdb ./backup_redis.rdb
```

### データのリストア

#### PostgreSQLのリストア

```bash
# バックアップから復元
cat backup_postgres.sql | docker exec -i local_postgres psql -U postgres mydb
```

#### MongoDBのリストア

```bash
# バックアップをコンテナにコピー
docker cp ./backup_mongodb local_mongodb:/tmp/backup

# リストア
docker exec local_mongodb mongorestore --username admin --password admin --authenticationDatabase admin /tmp/backup
```

### データの完全リセット

```bash
# 全データを削除して再起動
docker-compose down -v
docker-compose up -d

# 特定のデータベースのみリセット
docker-compose stop postgres
docker volume rm local_databases_postgres_data
docker-compose up -d postgres
```

---

## 🌐 ネットワーク

### コンテナ間通信

全てのコンテナは同一のDockerネットワーク内で動作しています。

**ホスト（Mac）からアクセス:**
```
PostgreSQL:  localhost:5432
Redis:       localhost:6379
MongoDB:     localhost:27017
Qdrant:      localhost:6333
```

**コンテナ間でアクセス:**
```
PostgreSQL:  postgres:5432
Redis:       redis:6379
MongoDB:     mongodb:27017
Qdrant:      qdrant:6333
```

### ポートマッピング

| サービス | コンテナ内ポート | ホストポート |
|---------|----------------|-------------|
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| MongoDB | 27017 | 27017 |
| Qdrant REST | 6333 | 6333 |
| Qdrant gRPC | 6334 | 6334 |
| Adminer | 8080 | 8080 |
| Mongo Express | 8081 | 8081 |
| Redis Commander | 8081 | 8082 |

---

## 🔍 デバッグ・トラブルシューティング

### コンテナ内に入る

```bash
# PostgreSQLコンテナに入る
docker exec -it local_postgres bash

# 直接psqlを起動
docker exec -it local_postgres psql -U postgres -d mydb

# Redisコンテナに入る
docker exec -it local_redis sh

# 直接redis-cliを起動
docker exec -it local_redis redis-cli

# MongoDBコンテナに入る
docker exec -it local_mongodb bash

# 直接mongoshを起動
docker exec -it local_mongodb mongosh -u admin -p admin
```

### リソース使用状況確認

```bash
# 全コンテナのリソース使用状況
docker stats

# 特定のコンテナのみ
docker stats local_postgres local_mongodb
```

### コンテナの詳細情報

```bash
# コンテナの設定を確認
docker inspect local_postgres

# ネットワーク設定を確認
docker inspect local_postgres | grep -A 20 Networks

# マウント情報を確認
docker inspect local_postgres | grep -A 10 Mounts
```

---

## 🛠️ カスタマイズ

### 環境変数の変更

`.env` ファイルを編集:

```bash
# データベース接続情報
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://admin:admin@localhost:27017/mydb?authSource=admin
QDRANT_URL=http://localhost:6333

# プロジェクト名
COMPOSE_PROJECT_NAME=local_databases
```

### ポート番号の変更

`docker-compose.yml` を編集:

```yaml
postgres:
  ports:
    - "15432:5432"  # ホスト側のポートを15432に変更
```

変更後、再起動:
```bash
docker-compose down
docker-compose up -d
```

### メモリ・CPU制限

`docker-compose.yml` に追加:

```yaml
postgres:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

---

## 📊 監視・モニタリング

### ヘルスチェック

```bash
# ヘルスチェックスクリプトを実行
./scripts/deployment/health-check.sh

# または手動でチェック
docker exec local_postgres pg_isready -U postgres
docker exec local_redis redis-cli ping
docker exec local_mongodb mongosh --eval "db.adminCommand('ping')"
curl http://localhost:6333/health
```

### ログレベルの変更

`docker-compose.yml` で環境変数を追加:

```yaml
postgres:
  environment:
    POSTGRES_LOG_STATEMENT: 'all'  # 全SQLをログ出力
```

---

## 🚨 よくある問題

### 問題1: コンテナが起動しない

```bash
# ログで原因を確認
docker-compose logs <サービス名>

# コンテナを完全に再作成
docker-compose down
docker-compose up -d --force-recreate
```

### 問題2: ポートが使用されている

```bash
# 使用中のポートを確認
lsof -i :5432

# docker-compose.ymlのポート番号を変更
# 例: "15432:5432"
```

### 問題3: データが消えた

```bash
# Volumeが残っているか確認
docker volume ls | grep local_databases

# データが残っていれば復旧可能
docker-compose up -d
```

### 問題4: ディスク容量不足

```bash
# 未使用のイメージ・コンテナ削除
docker system prune -a

# 未使用のVolumeも削除（注意！）
docker system prune -a --volumes
```

---

## 📝 ベストプラクティス

### 開発時

1. **docker-compose up -d** で起動
2. 作業終了後も起動したまま（次回すぐ使える）
3. 不要な時だけ **docker-compose down**

### データ保護

1. **定期的にバックアップ**を取る
2. **docker-compose down -v** は慎重に（全データ削除）
3. 重要なデータは外部にエクスポート

### パフォーマンス

1. 不要なサービスは起動しない
2. ログサイズを監視（`docker-compose logs` は肥大化する）
3. 定期的に `docker system prune` でクリーンアップ

---

## 🔗 関連ドキュメント

- [README.md](./README.md) - プロジェクト概要
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - 初回セットアップ手順
- [QUICKSTART.md](./QUICKSTART.md) - クイックスタート
- [DATABASES.md](./DATABASES.md) - データベース比較

---

## 📚 参考リンク

- [Docker Compose 公式ドキュメント](https://docs.docker.com/compose/)
- [Docker Volume 管理](https://docs.docker.com/storage/volumes/)
- [Docker ネットワーク](https://docs.docker.com/network/)
