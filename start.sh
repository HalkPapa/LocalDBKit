#!/bin/bash

echo "================================================"
echo "  ローカルデータベース環境を起動しています..."
echo "================================================"

# Docker コマンドが存在するか確認
if ! command -v docker &> /dev/null; then
    echo ""
    echo "❌ エラー: Dockerコマンドが見つかりません"
    echo ""
    echo "以下のいずれかをインストールしてください:"
    echo ""
    echo "  オプション1: Colima（推奨・軽量）"
    echo "    brew install colima docker docker-compose"
    echo "    colima start"
    echo ""
    echo "  オプション2: Docker Desktop"
    echo "    brew install --cask docker"
    echo ""
    echo "詳細: SETUP_GUIDE.md を参照"
    exit 1
fi

# Docker デーモンが起動しているか確認
if ! docker info > /dev/null 2>&1; then
    echo ""
    echo "❌ エラー: Dockerデーモンが起動していません"
    echo ""

    # Colimaがインストールされているか確認
    if command -v colima &> /dev/null; then
        echo "Colimaを起動中..."
        colima start

        # 起動を待つ
        echo "起動を待機中..."
        sleep 5

        # 再度確認
        if docker info > /dev/null 2>&1; then
            echo "✅ Colimaが起動しました"
        else
            echo "❌ Colimaの起動に失敗しました"
            echo "手動で起動してください: colima start"
            exit 1
        fi
    else
        echo "以下のいずれかを実行してください:"
        echo ""
        echo "  Colimaの場合:"
        echo "    colima start"
        echo ""
        echo "  Docker Desktopの場合:"
        echo "    open -a Docker"
        echo ""
        echo "起動後、再度このスクリプトを実行してください"
        exit 1
    fi
fi

# docker-compose コマンドの確認
if ! command -v docker-compose &> /dev/null; then
    echo ""
    echo "❌ エラー: docker-compose コマンドが見つかりません"
    echo "インストール: brew install docker-compose"
    exit 1
fi

# docker-compose.yml の存在確認
if [ ! -f "docker-compose.yml" ]; then
    echo ""
    echo "❌ エラー: docker-compose.yml が見つかりません"
    echo "正しいディレクトリで実行してください"
    echo "現在のディレクトリ: $(pwd)"
    exit 1
fi

# データベースコンテナを起動
echo ""
echo "データベースコンテナを起動中..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ エラー: コンテナの起動に失敗しました"
    echo "ログを確認: docker-compose logs"
    exit 1
fi

# 起動待機
echo ""
echo "サービスの起動を待機中..."
sleep 8

# 状態確認
echo ""
echo "コンテナ状態:"
docker-compose ps

echo ""
echo "================================================"
echo "  ✅ データベース環境が起動しました！"
echo "================================================"
echo ""
echo "📊 管理ツール:"
echo "  - Adminer (DB管理):    http://localhost:8080"
echo "  - Qdrant Dashboard:    http://localhost:6333/dashboard"
echo ""
echo "🔌 接続情報:"
echo "  - PostgreSQL:  localhost:5432"
echo "  - Redis:       localhost:6379"
echo "  - MongoDB:     localhost:27017"
echo "  - Qdrant:      localhost:6333"
echo ""
echo "📚 使用例:"
echo "  - Python: examples/*/python_example.py"
echo "  - Node.js: examples/postgres/nodejs_example.js"
echo ""
echo "🛑 停止: docker-compose down"
echo "📋 ログ: docker-compose logs -f"
echo "🔍 ヘルスチェック: ./health-check.sh"
echo ""
echo "詳細なガイド: SETUP_GUIDE.md"
echo ""
