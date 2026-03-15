# バックアップガイド

LocalDBKitのバックアップ・リストア機能の完全ガイドです。

## 🎯 概要

LocalDBKitは以下のデータベースのバックアップをサポートしています：

- PostgreSQL（pgvector含む）
- MongoDB
- Redis
- Qdrant

## 📦 手動バックアップ

### 基本的な使い方

```bash
# バックアップ実行
make backup

# または
./scripts/deployment/backup.sh

# カスタムディレクトリ指定
./scripts/deployment/backup.sh /path/to/backup/dir
```

### バックアップ内容

バックアップには以下が含まれます：

```
backups/20260315_120000/
├── postgres_backup.sql          # PostgreSQL全データ
├── mongodb_backup.archive.gz    # MongoDB全データ（圧縮）
├── redis_dump.rdb              # Redisスナップショット
├── qdrant_storage/             # Qdrant全データ
└── backup_metadata.json        # メタデータ
```

## 🔄 リストア

### 基本的な使い方

```bash
# リストア実行（インタラクティブ）
make restore BACKUP=./backups/20260315_120000

# または
./scripts/deployment/restore.sh ./backups/20260315_120000
```

### 注意事項

⚠️ **警告**: リストアは既存のデータを上書きします！

- リストア前に現在のデータをバックアップすることを推奨
- 確認プロンプトで慎重に確認
- テスト環境で事前確認

## ⏰ 自動バックアップ

### cron設定

#### macOS / Linux

```bash
# crontab編集
crontab -e

# 毎日午前2時にバックアップ実行
0 2 * * * /Users/koikedaisuke/MyProjects/データベース構築/scripts/deployment/auto-backup.sh

# 毎週日曜日午前3時にバックアップ実行
0 3 * * 0 /Users/koikedaisuke/MyProjects/データベース構築/scripts/deployment/auto-backup.sh

# 12時間ごとにバックアップ実行
0 */12 * * * /Users/koikedaisuke/MyProjects/データベース構築/scripts/deployment/auto-backup.sh
```

#### 環境変数設定

```bash
# バックアップ保存先
export BACKUP_DIR="/path/to/backups"

# 保持期間（日数）デフォルト: 7日
export RETENTION_DAYS=30

# cron設定（環境変数を使用）
0 2 * * * BACKUP_DIR=/mnt/backups RETENTION_DAYS=30 /path/to/auto-backup.sh
```

### ログ確認

```bash
# バックアップログ表示
tail -f logs/backup.log

# 最新100行表示
tail -100 logs/backup.log
```

## 📊 バックアップ管理

### バックアップ一覧

```bash
# バックアップ一覧表示
ls -lh backups/

# サイズ順にソート
du -sh backups/* | sort -h
```

### 古いバックアップ削除

```bash
# 7日以前のバックアップを削除
find backups/ -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

# 30日以前のバックアップを削除
find backups/ -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

### ディスク使用量確認

```bash
# バックアップディレクトリのサイズ
du -sh backups/

# 各バックアップのサイズ
du -sh backups/*
```

## ☁️ クラウドバックアップ

### AWS S3

```bash
# AWS CLI設定
aws configure

# S3にアップロード
aws s3 sync backups/ s3://my-bucket/localdbkit-backups/

# 自動化（cron）
0 3 * * * /path/to/auto-backup.sh && aws s3 sync backups/ s3://my-bucket/backups/
```

### Rclone（汎用クラウドストレージ）

```bash
# Rcloneインストール
brew install rclone  # macOS
# apt install rclone  # Linux

# 設定
rclone config

# 同期
rclone sync backups/ remote:localdbkit-backups/

# 自動化（cron）
0 3 * * * /path/to/auto-backup.sh && rclone sync backups/ remote:backups/
```

## 🧪 バックアップテスト

定期的にバックアップが正常にリストアできるかテストすることを推奨します。

### テスト手順

```bash
# 1. 現在のデータをバックアップ
make backup

# 2. テストデータを作成
docker exec -it local_postgres psql -U postgres -c "CREATE TABLE test_table (id INT);"

# 3. バックアップからリストア
make restore BACKUP=./backups/20260315_120000

# 4. データ確認
docker exec -it local_postgres psql -U postgres -c "\dt"

# 5. test_tableが存在しないことを確認（リストア成功）
```

## 📋 ベストプラクティス

### 推奨設定

1. **毎日自動バックアップ**
   - 深夜時間帯に実行
   - 負荷の少ない時間を選択

2. **バックアップ保持期間**
   - 日次: 7日間
   - 週次: 4週間
   - 月次: 12ヶ月

3. **オフサイトバックアップ**
   - クラウドストレージに同期
   - 物理的に異なる場所に保存

4. **定期的なテスト**
   - 月1回リストアテスト
   - ディザスタリカバリ手順確認

### トラブルシューティング

#### バックアップ失敗

```bash
# Dockerコンテナ状態確認
docker compose ps

# ログ確認
docker compose logs postgres
docker compose logs mongodb

# ディスク容量確認
df -h
```

#### リストア失敗

```bash
# バックアップファイル確認
ls -lh backups/20260315_120000/

# metadata確認
cat backups/20260315_120000/backup_metadata.json

# 手動リストア（PostgreSQL例）
docker exec -i local_postgres psql -U postgres < backups/20260315_120000/postgres_backup.sql
```

## 🔐 セキュリティ

### バックアップの暗号化

```bash
# バックアップを暗号化
tar czf - backups/20260315_120000 | openssl enc -aes-256-cbc -salt -out backup.tar.gz.enc

# 復号化
openssl enc -aes-256-cbc -d -in backup.tar.gz.enc | tar xz
```

### アクセス制限

```bash
# バックアップディレクトリの権限設定
chmod 700 backups/
chmod 600 backups/*/postgres_backup.sql
```

---

**作成日**: 2026年3月15日
**最終更新**: 2026年3月15日
