#!/bin/bash

# 自動バックアップスクリプト
# cron設定例: 0 2 * * * /path/to/auto-backup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
LOG_FILE="$PROJECT_ROOT/logs/backup.log"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# ログディレクトリ作成
mkdir -p "$(dirname "$LOG_FILE")"

# ログ関数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "自動バックアップ開始"
log "=========================================="

# バックアップ実行
log "バックアップを実行中..."
cd "$PROJECT_ROOT"
if ./scripts/deployment/backup.sh "$BACKUP_DIR" >> "$LOG_FILE" 2>&1; then
    log "✅ バックアップ成功"
else
    log "❌ バックアップ失敗"
    exit 1
fi

# 古いバックアップの削除
log "古いバックアップを削除中（${RETENTION_DAYS}日以前）..."
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

# バックアップ数確認
BACKUP_COUNT=$(find "$BACKUP_DIR" -maxdepth 1 -type d | wc -l | tr -d ' ')
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "0B")

log "📊 バックアップ統計:"
log "   - 保存数: $BACKUP_COUNT"
log "   - 合計サイズ: $BACKUP_SIZE"
log "   - 保持期間: ${RETENTION_DAYS}日"

log "=========================================="
log "自動バックアップ完了"
log "=========================================="
