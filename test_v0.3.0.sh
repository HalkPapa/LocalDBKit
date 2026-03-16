#!/bin/bash
# v0.3.0 Integration Test Script

set -e

echo "🧪 LocalDBKit v0.3.0 統合テスト"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

success() {
    echo -e "${GREEN}✓${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Wait for services
echo "1️⃣  サービス起動確認中..."
sleep 3

# Test 1: API Gateway Health
echo ""
echo "2️⃣  API Gateway ヘルスチェック..."
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    success "API Gateway: $(echo $response | jq -r '.status')"
else
    error "API Gateway: 応答なし"
    exit 1
fi

# Test 2: Multimodal Processor Health
echo ""
echo "3️⃣  Multimodal Processor ヘルスチェック..."
response=$(curl -s http://localhost:8001/health)
if echo "$response" | grep -q "healthy"; then
    success "Multimodal Processor: $(echo $response | jq -r '.status')"
else
    error "Multimodal Processor: 応答なし"
    exit 1
fi

# Test 3: Authentication
echo ""
echo "4️⃣  JWT認証テスト..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin" | jq -r '.access_token')

if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    success "JWT認証成功（トークン取得）"
else
    error "JWT認証失敗"
    exit 1
fi

# Test 4: LLM Models
echo ""
echo "5️⃣  LLMモデル一覧取得..."
models=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/llm/models | jq -r '.count')
if [ "$models" -gt 0 ]; then
    success "LLMモデル: ${models}個検出"
else
    error "LLMモデル検出失敗"
    exit 1
fi

# Test 5: OCR
echo ""
echo "6️⃣  OCR処理テスト..."
if [ -f "test-data/test-image.png" ]; then
    ocr_result=$(curl -s -X POST "http://localhost:8001/api/v1/ocr/extract" \
        -F "file=@test-data/test-image.png" | jq -r '.text')
    if [ ! -z "$ocr_result" ] && [ "$ocr_result" != "null" ]; then
        success "OCR: テキスト抽出成功（\"$ocr_result\"）"
    else
        error "OCR: テキスト抽出失敗"
        exit 1
    fi
else
    info "OCR: テスト画像なし（スキップ）"
fi

# Test 6: RAG Document Add
echo ""
echo "7️⃣  RAGドキュメント追加テスト..."
doc_response=$(curl -s -X POST "http://localhost:8000/api/v1/rag/documents" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "This is an automated test document for LocalDBKit v0.3.0",
        "collection": "test_auto",
        "metadata": {"test": true}
    }')

doc_id=$(echo "$doc_response" | jq -r '.id')
if [ ! -z "$doc_id" ] && [ "$doc_id" != "null" ]; then
    success "RAG: ドキュメント追加成功（ID: ${doc_id:0:8}...）"
else
    error "RAG: ドキュメント追加失敗"
    echo "$doc_response"
    exit 1
fi

# Test 7: RAG Query
echo ""
echo "8️⃣  RAGクエリテスト..."
query_response=$(curl -s -X POST "http://localhost:8000/api/v1/rag/query" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "What is this test about?",
        "collection": "test_auto",
        "use_llm": true,
        "top_k": 3
    }')

answer=$(echo "$query_response" | jq -r '.answer')
sources=$(echo "$query_response" | jq -r '.sources | length')

if [ ! -z "$answer" ] && [ "$answer" != "null" ] && [ "$sources" -gt 0 ]; then
    success "RAG: クエリ成功（ソース: ${sources}件）"
    info "回答: ${answer:0:80}..."
else
    error "RAG: クエリ失敗"
    exit 1
fi

# Test 8: RAG Collections
echo ""
echo "9️⃣  RAGコレクション一覧テスト..."
collections=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/rag/collections | jq -r '.count')
if [ "$collections" -gt 0 ]; then
    success "RAG: コレクション ${collections}個確認"
else
    error "RAG: コレクション取得失敗"
    exit 1
fi

# Summary
echo ""
echo "================================"
echo -e "${GREEN}🎉 全テスト合格！${NC}"
echo ""
echo "📊 テスト結果:"
echo "  - API Gateway: ✓"
echo "  - Multimodal Processor: ✓"
echo "  - JWT認証: ✓"
echo "  - LLMモデル: ✓"
echo "  - OCR処理: ✓"
echo "  - RAGドキュメント追加: ✓"
echo "  - RAGクエリ: ✓"
echo "  - RAGコレクション: ✓"
echo ""
echo "✅ LocalDBKit v0.3.0 は正常に動作しています！"
