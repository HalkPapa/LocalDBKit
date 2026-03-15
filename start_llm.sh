#!/bin/bash

# LLMシステム起動スクリプト
# 作成者: Claude Sonnet 4.5 (Anthropic)
# 作成日: 2026年3月11日

set -e

# 色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ローカルLLMシステム起動${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Dockerチェック
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Dockerが見つかりません${NC}"
    echo "Dockerをインストールしてください"
    exit 1
fi

# docker-composeチェック
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-composeが見つかりません${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker環境OK${NC}"

# Ollamaコンテナ起動
echo ""
echo -e "${BLUE}[1/3] Ollamaコンテナ起動中...${NC}"
docker-compose up -d ollama

# Ollama起動待機
echo -e "${YELLOW}  Ollamaの起動を待機中...${NC}"
sleep 5

# Ollama接続確認
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${GREEN}  ✓ Ollama起動完了${NC}"
else
    echo -e "${YELLOW}  ⚠ Ollamaへの接続に失敗しました${NC}"
    echo -e "  docker logs local_ollama でログを確認してください"
fi

# モデル確認
echo ""
echo -e "${BLUE}[2/3] インストール済みモデル確認${NC}"
MODELS=$(docker exec local_ollama ollama list 2>/dev/null | tail -n +2)

if [ -z "$MODELS" ]; then
    echo -e "${YELLOW}  ⚠ モデルがインストールされていません${NC}"
    echo ""
    echo -e "  推奨モデルをインストールしますか？"
    echo -e "  ${GREEN}llama3.2${NC} (3B, バランス型)"
    echo ""
    read -p "  インストールしますか? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}  モデルダウンロード中...（1-5分かかります）${NC}"
        docker exec -it local_ollama ollama pull llama3.2
        echo -e "${GREEN}  ✓ モデルインストール完了${NC}"
    else
        echo -e "${YELLOW}  後で手動でインストールしてください:${NC}"
        echo -e "  ${GREEN}docker exec -it local_ollama ollama pull llama3.2${NC}"
    fi
else
    echo -e "${GREEN}  ✓ インストール済みモデル:${NC}"
    echo "$MODELS" | sed 's/^/    /'
fi

# データベース起動確認
echo ""
echo -e "${BLUE}[3/3] データベース起動確認${NC}"

# MongoDB
if docker ps | grep -q local_mongodb; then
    echo -e "${GREEN}  ✓ MongoDB起動中${NC}"
else
    echo -e "${YELLOW}  ⚠ MongoDBが起動していません${NC}"
    docker-compose up -d mongodb
fi

# Qdrant
if docker ps | grep -q local_qdrant; then
    echo -e "${GREEN}  ✓ Qdrant起動中${NC}"
else
    echo -e "${YELLOW}  ⚠ Qdrantが起動していません${NC}"
    docker-compose up -d qdrant
fi

# 完了
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ セットアップ完了！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo ""
echo -e "1. チャットアプリ起動:"
echo -e "   ${YELLOW}streamlit run llm_apps/chat_app.py${NC}"
echo ""
echo -e "2. RAGアプリ起動:"
echo -e "   ${YELLOW}streamlit run llm_apps/rag_app.py${NC}"
echo ""
echo -e "3. ブラウザで開く:"
echo -e "   ${YELLOW}http://localhost:8501${NC}"
echo ""
echo -e "${BLUE}ドキュメント:${NC} LLM_GUIDE.md"
echo ""
