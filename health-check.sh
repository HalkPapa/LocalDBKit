#!/bin/bash

echo "================================================"
echo "  データベース ヘルスチェック"
echo "================================================"

# Docker デーモンチェック
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker デーモンが起動していません"
    echo "   Docker Desktop を起動してください"
    exit 1
fi

echo "✅ Docker デーモン: 起動中"
echo ""

# コンテナ状態チェック
echo "📦 コンテナ状態:"
docker-compose ps
echo ""

# PostgreSQL
echo "🐘 PostgreSQL チェック..."
if docker exec local_postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL: 正常"
else
    echo "   ❌ PostgreSQL: 応答なし"
fi

# Redis
echo "🔴 Redis チェック..."
if docker exec local_redis redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis: 正常"
else
    echo "   ❌ Redis: 応答なし"
fi

# MongoDB
echo "🍃 MongoDB チェック..."
if docker exec local_mongodb mongosh --eval "db.adminCommand('ping')" --quiet > /dev/null 2>&1; then
    echo "   ✅ MongoDB: 正常"
else
    echo "   ❌ MongoDB: 応答なし"
fi

# Qdrant
echo "🎯 Qdrant チェック..."
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "   ✅ Qdrant: 正常"
else
    echo "   ❌ Qdrant: 応答なし"
fi

echo ""
echo "================================================"
echo "  管理ツール:"
echo "  - Adminer: http://localhost:8080"
echo "  - Qdrant Dashboard: http://localhost:6333/dashboard"
echo "================================================"
