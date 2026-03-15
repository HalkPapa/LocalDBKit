#!/bin/bash

# データベースバックアップスクリプト
# Usage: ./scripts/deployment/backup.sh [backup_dir]

set -e

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"

echo "================================================"
echo "  LocalDBKit バックアップ"
echo "================================================"
echo "📁 バックアップ先: $BACKUP_PATH"
echo ""

# バックアップディレクトリ作成
mkdir -p "$BACKUP_PATH"

# PostgreSQL バックアップ
echo "🐘 PostgreSQL をバックアップ中..."
docker exec local_postgres pg_dumpall -U postgres > "$BACKUP_PATH/postgres_backup.sql"
echo "   ✅ PostgreSQL: $BACKUP_PATH/postgres_backup.sql"

# MongoDB バックアップ
echo "🍃 MongoDB をバックアップ中..."
docker exec local_mongodb mongodump --archive --gzip --username admin --password admin --authenticationDatabase admin > "$BACKUP_PATH/mongodb_backup.archive.gz"
echo "   ✅ MongoDB: $BACKUP_PATH/mongodb_backup.archive.gz"

# Redis バックアップ
echo "🔴 Redis をバックアップ中..."
docker exec local_redis redis-cli --rdb /data/dump.rdb SAVE > /dev/null
docker cp local_redis:/data/dump.rdb "$BACKUP_PATH/redis_dump.rdb"
echo "   ✅ Redis: $BACKUP_PATH/redis_dump.rdb"

# Qdrant バックアップ
echo "🎯 Qdrant をバックアップ中..."
if docker exec local_qdrant test -d /qdrant/storage; then
    docker cp local_qdrant:/qdrant/storage "$BACKUP_PATH/qdrant_storage"
    echo "   ✅ Qdrant: $BACKUP_PATH/qdrant_storage"
else
    echo "   ⚠️  Qdrant: データなし（スキップ）"
fi

# メタデータ保存
echo "📝 メタデータを保存中..."
cat > "$BACKUP_PATH/backup_metadata.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "databases": {
    "postgresql": "postgres_backup.sql",
    "mongodb": "mongodb_backup.archive.gz",
    "redis": "redis_dump.rdb",
    "qdrant": "qdrant_storage"
  }
}
EOF
echo "   ✅ メタデータ: $BACKUP_PATH/backup_metadata.json"

# バックアップサイズ計算
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)

echo ""
echo "================================================"
echo "✅ バックアップ完了"
echo "================================================"
echo "📁 保存先: $BACKUP_PATH"
echo "💾 サイズ: $BACKUP_SIZE"
echo ""
echo "リストア方法:"
echo "  ./scripts/deployment/restore.sh $BACKUP_PATH"
echo "================================================"
