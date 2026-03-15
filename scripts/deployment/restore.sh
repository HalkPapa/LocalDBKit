#!/bin/bash

# データベースリストアスクリプト
# Usage: ./scripts/deployment/restore.sh <backup_path>

set -e

if [ -z "$1" ]; then
    echo "エラー: バックアップパスを指定してください"
    echo "使用例: ./scripts/deployment/restore.sh ./backups/20260315_120000"
    exit 1
fi

BACKUP_PATH="$1"

if [ ! -d "$BACKUP_PATH" ]; then
    echo "エラー: バックアップディレクトリが見つかりません: $BACKUP_PATH"
    exit 1
fi

echo "================================================"
echo "  LocalDBKit リストア"
echo "================================================"
echo "📁 バックアップ元: $BACKUP_PATH"
echo ""
echo "⚠️  警告: 現在のデータは上書きされます"
read -p "続行しますか？ (y/N): " confirm
if [ "$confirm" != "y" ]; then
    echo "キャンセルしました"
    exit 0
fi
echo ""

# PostgreSQL リストア
if [ -f "$BACKUP_PATH/postgres_backup.sql" ]; then
    echo "🐘 PostgreSQL をリストア中..."
    docker exec -i local_postgres psql -U postgres < "$BACKUP_PATH/postgres_backup.sql" > /dev/null 2>&1
    echo "   ✅ PostgreSQL リストア完了"
else
    echo "   ⚠️  PostgreSQL: バックアップファイルなし"
fi

# MongoDB リストア
if [ -f "$BACKUP_PATH/mongodb_backup.archive.gz" ]; then
    echo "🍃 MongoDB をリストア中..."
    docker exec -i local_mongodb mongorestore --archive --gzip --username admin --password admin --authenticationDatabase admin --drop < "$BACKUP_PATH/mongodb_backup.archive.gz" > /dev/null 2>&1
    echo "   ✅ MongoDB リストア完了"
else
    echo "   ⚠️  MongoDB: バックアップファイルなし"
fi

# Redis リストア
if [ -f "$BACKUP_PATH/redis_dump.rdb" ]; then
    echo "🔴 Redis をリストア中..."
    docker cp "$BACKUP_PATH/redis_dump.rdb" local_redis:/data/dump.rdb
    docker exec local_redis redis-cli SHUTDOWN NOSAVE || true
    sleep 2
    docker restart local_redis > /dev/null
    sleep 2
    echo "   ✅ Redis リストア完了"
else
    echo "   ⚠️  Redis: バックアップファイルなし"
fi

# Qdrant リストア
if [ -d "$BACKUP_PATH/qdrant_storage" ]; then
    echo "🎯 Qdrant をリストア中..."
    docker stop local_qdrant > /dev/null
    docker cp "$BACKUP_PATH/qdrant_storage/." local_qdrant:/qdrant/storage/
    docker start local_qdrant > /dev/null
    sleep 2
    echo "   ✅ Qdrant リストア完了"
else
    echo "   ⚠️  Qdrant: バックアップディレクトリなし"
fi

# メタデータ表示
if [ -f "$BACKUP_PATH/backup_metadata.json" ]; then
    echo ""
    echo "📝 バックアップ情報:"
    cat "$BACKUP_PATH/backup_metadata.json" | grep -E "(timestamp|date)" | sed 's/^/   /'
fi

echo ""
echo "================================================"
echo "✅ リストア完了"
echo "================================================"
