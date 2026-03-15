#!/bin/bash

# 全アプリ・ゲーム一覧表示スクリプト
# 作成者: Claude Sonnet 4.5 (Anthropic)
# 作成日: 2026年3月9日

# 色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  データベース一覧${NC}"
echo -e "${BLUE}========================================${NC}"

# PostgreSQL
echo ""
echo -e "${GREEN}=== PostgreSQL Databases ===${NC}"
docker exec local_postgres psql -U postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres'" | sed 's/^/  - /'

# MongoDB
echo ""
echo -e "${GREEN}=== MongoDB Databases ===${NC}"
docker exec local_mongodb mongosh -u admin -p admin --quiet --eval "
db.adminCommand('listDatabases').databases.forEach(function(d){
    if (d.name !== 'admin' && d.name !== 'config' && d.name !== 'local') {
        print('  - ' + d.name);
    }
});
"

# Redis (キープレフィックス)
echo ""
echo -e "${GREEN}=== Redis Key Prefixes ===${NC}"
PREFIXES=$(docker exec local_redis redis-cli --scan --pattern "*:*" 2>/dev/null | cut -d: -f1 | sort -u)
if [ -z "$PREFIXES" ]; then
    echo -e "  ${YELLOW}(キープレフィックスなし)${NC}"
else
    echo "$PREFIXES" | sed 's/^/  - /' | sed 's/$/:*/'
fi

# Qdrant
echo ""
echo -e "${GREEN}=== Qdrant Collections ===${NC}"
COLLECTIONS=$(curl -s http://localhost:6333/collections 2>/dev/null | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
if [ -z "$COLLECTIONS" ]; then
    echo -e "  ${YELLOW}(コレクションなし)${NC}"
else
    echo "$COLLECTIONS" | sed 's/^/  - /'
fi

echo ""
echo -e "${BLUE}========================================${NC}"
