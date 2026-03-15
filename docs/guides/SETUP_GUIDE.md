# セットアップガイド（完全版）

このガイドでは、ゼロからローカルデータベース環境を構築する手順を説明します。

---

## 📋 目次

1. [Docker環境のセットアップ](#1-docker環境のセットアップ)
2. [データベースの起動](#2-データベースの起動)
3. [動作確認](#3-動作確認)
4. [日常的な使い方](#4-日常的な使い方)
5. [よくある問題と解決方法](#5-よくある問題と解決方法)

---

## 1. Docker環境のセットアップ

### 1-1. 現在の環境を確認

ターミナルで以下を実行:
```bash
docker --version
```

- **コマンドが見つかる**: Docker環境が既にあります → [1-3へ](#1-3-dockerデーモンの起動確認)
- **コマンドが見つからない**: Docker環境をインストールする必要があります → [1-2へ](#1-2-docker環境のインストール)

### 1-2. Docker環境のインストール

以下の2つの選択肢があります。**Colimaを推奨**します。

#### オプションA: Colima（推奨）

**メリット:**
- 軽量（メモリ使用量が少ない）
- 管理者権限不要
- 起動が速い

**インストール手順:**
```bash
# Homebrewでインストール
brew install colima docker docker-compose

# 完了確認
colima version
docker --version
docker-compose --version
```

#### オプションB: Docker Desktop

**メリット:**
- 公式のDocker環境
- GUI管理ツール付き

**デメリット:**
- メモリ使用量が多い
- インストールに管理者権限が必要

**インストール手順:**
```bash
# Homebrewでインストール（パスワード入力が必要）
brew install --cask docker
```

または、公式サイトからダウンロード:
https://www.docker.com/products/docker-desktop/

### 1-3. Dockerデーモンの起動確認

以下のコマンドで確認:
```bash
docker ps
```

#### 成功した場合
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```
→ Dockerデーモンが起動しています。[2. データベースの起動](#2-データベースの起動)へ進んでください。

#### エラーが出る場合
```
Cannot connect to the Docker daemon at unix:///...
```
→ Dockerデーモンを起動する必要があります。

**Colimaの場合:**
```bash
colima start
```

**Docker Desktopの場合:**
```bash
# GUIから起動
open -a Docker

# または、アプリケーションフォルダから「Docker.app」をダブルクリック
```

起動には30秒〜1分かかります。以下で確認:
```bash
# 起動完了を確認
docker ps
```

---

## 2. データベースの起動

### 2-1. プロジェクトディレクトリに移動

```bash
cd /Users/koikedaisuke/MyProjects/データベース構築
```

### 2-2. データベースコンテナを起動

以下のいずれかの方法で起動:

**方法1: 起動スクリプトを使う（推奨）**
```bash
./start.sh
```

**方法2: docker-composeコマンドを直接使う**
```bash
docker-compose up -d
```

### 2-3. 起動完了を待つ

**初回起動の場合:**
- イメージのダウンロード: 1〜2分
- コンテナの起動: 30秒〜1分
- **合計: 2〜3分**

**2回目以降:**
- コンテナの起動: 5〜10秒

### 2-4. 起動状態を確認

```bash
# 起動中のコンテナを確認
docker ps

# または、ヘルスチェックスクリプトを実行
./health-check.sh
```

**期待される出力（docker ps）:**
```
CONTAINER ID   IMAGE                    STATUS
...            ankane/pgvector:latest   Up 30 seconds
...            redis:7-alpine           Up 30 seconds
...            mongo:7                  Up 30 seconds
...            qdrant/qdrant:latest     Up 30 seconds
...            adminer:latest           Up 30 seconds
```

5つのコンテナが「Up」状態になっていれば成功です。

---

## 3. 動作確認

### 3-1. ブラウザでアクセス

以下のURLをブラウザで開く:

1. **Adminer（データベース管理UI）**: http://localhost:8080
2. **Qdrant Dashboard**: http://localhost:6333/dashboard

両方開ければ、データベースは正常に起動しています。

### 3-2. サンプルコードで確認

```bash
# Python依存関係をインストール（初回のみ）
pip install -r requirements.txt

# PostgreSQLの動作確認
python examples/postgres/python_example.py

# Redisの動作確認
python examples/redis/python_example.py

# MongoDBの動作確認
python examples/mongodb/python_example.py

# Qdrantの動作確認
python examples/qdrant/python_example.py
```

エラーなく実行できれば、全てのデータベースが正常に動作しています。

---

## 4. 日常的な使い方

### 起動

```bash
# Docker環境を起動（Colimaの場合のみ必要）
colima start

# データベースを起動
cd /Users/koikedaisuke/MyProjects/データベース構築
docker-compose up -d
```

### 停止

```bash
# データベースを停止
docker-compose down

# Docker環境も停止する場合（Colimaの場合）
colima stop
```

### 再起動

```bash
# 全てのデータベースを再起動
docker-compose restart

# 特定のデータベースのみ再起動
docker-compose restart postgres
```

### ログ確認

```bash
# 全てのログを表示
docker-compose logs

# リアルタイムでログを監視
docker-compose logs -f

# 特定のサービスのログのみ
docker-compose logs postgres
docker-compose logs redis
```

### データのリセット

```bash
# データを完全に削除して再起動
docker-compose down -v
docker-compose up -d
```

---

## 5. よくある問題と解決方法

### ❌ 問題1: `docker: command not found`

**原因**: Dockerがインストールされていない

**解決方法**: [1-2. Docker環境のインストール](#1-2-docker環境のインストール)を参照

---

### ❌ 問題2: `Cannot connect to the Docker daemon`

**原因**: Dockerデーモンが起動していない

**解決方法**:

Colimaの場合:
```bash
colima start
```

Docker Desktopの場合:
```bash
open -a Docker
```

起動を待ってから再度実行:
```bash
docker ps
```

---

### ❌ 問題3: `docker ps` でコンテナが表示されない

**原因**: コンテナが起動していない

**解決方法**:
```bash
# 正しいディレクトリにいるか確認
pwd
# /Users/koikedaisuke/MyProjects/データベース構築 であるべき

# コンテナを起動
docker-compose up -d

# 確認
docker ps
```

---

### ❌ 問題4: `Connection refused` エラー

**原因**: データベースコンテナが起動していない、または起動中

**解決方法**:
```bash
# コンテナの状態を確認
docker ps

# コンテナが「Up」状態か確認
# 起動直後の場合は30秒ほど待つ
sleep 30

# ヘルスチェック実行
./health-check.sh

# それでも接続できない場合は再起動
docker-compose restart
```

---

### ❌ 問題5: `port is already allocated`

**原因**: ポートが他のプロセスに使用されている

**解決方法**:

使用中のポートを確認:
```bash
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :27017 # MongoDB
lsof -i :6333  # Qdrant
```

以下のいずれかを実行:
1. 使用中のプロセスを停止
2. `docker-compose.yml` のポート番号を変更（例: `"15432:5432"`）

---

### ❌ 問題6: Colimaが起動しない

**解決方法**:
```bash
# Colimaを停止
colima stop

# 完全にリセット
colima delete

# 再起動（CPUとメモリを指定）
colima start --cpu 4 --memory 8
```

---

## 📚 次のステップ

セットアップが完了したら:

1. [DATABASES.md](./DATABASES.md) - 各データベースの使い分けガイド
2. [README.md](./README.md) - 詳細な使い方とリファレンス
3. `examples/` ディレクトリ - 各データベースのサンプルコード

---

## 🆘 サポート

問題が解決しない場合:

1. ログを確認: `docker-compose logs`
2. GitHub Issues: https://github.com/anthropics/claude-code/issues
3. Docker公式ドキュメント: https://docs.docker.com/
4. Colima公式ドキュメント: https://github.com/abiosoft/colima

---

**注意**: このセットアップは開発環境専用です。本番環境では適切なセキュリティ設定を行ってください。
