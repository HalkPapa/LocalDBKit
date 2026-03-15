# ローカルLLMシステムガイド

**作成者**: Claude Sonnet 4.5 (Anthropic)
**作成日**: 2026年3月11日
**バージョン**: 1.0

このガイドは、Ollama（ローカルLLM）を使った完全プライベートなAIシステムの使い方を説明します。

---

## 📋 目次

1. [概要](#概要)
2. [システム構成](#システム構成)
3. [セットアップ](#セットアップ)
4. [使い方](#使い方)
5. [アプリケーション](#アプリケーション)
6. [トラブルシューティング](#トラブルシューティング)
7. [推奨モデル](#推奨モデル)

---

## 🎯 概要

### できること

このシステムで以下ができます:

1. **チャットボット**
   - ローカルLLMとの会話
   - 会話履歴保存（MongoDB）
   - プライベート・オフライン動作

2. **RAG（検索拡張生成）**
   - 自分のドキュメントを学習
   - 質問に関連情報を検索して回答
   - ベクトル検索（Qdrant）

3. **セマンティック検索**
   - 自然言語でドキュメント検索
   - 意味的に類似した文書を発見

### 特徴

- ✅ **完全無料** - オープンソース、API不要
- ✅ **プライバシー保護** - 全てローカル処理
- ✅ **オフライン動作** - インターネット不要
- ✅ **カスタマイズ可能** - 自分のデータで学習

---

## 🏗️ システム構成

```
┌─────────────────────────────────────┐
│       Streamlit WebUI               │
│  - chat_app.py (チャット)           │
│  - rag_app.py (RAG)                 │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│       Ollama (ローカルLLM)          │
│  http://localhost:11434             │
│  - llama3.2 (推奨)                  │
│  - gemma2:2b                        │
│  - その他多数                        │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│       データベース                   │
│  - MongoDB (会話履歴)               │
│  - Qdrant (ベクトル検索)            │
│  - PostgreSQL (将来の拡張用)        │
└─────────────────────────────────────┘
```

### コンポーネント

| コンポーネント | 役割 | ポート |
|--------------|------|--------|
| **Ollama** | ローカルLLM実行環境 | 11434 |
| **Streamlit** | WebUI | 8501 |
| **MongoDB** | 会話履歴保存 | 27017 |
| **Qdrant** | ベクトル検索 | 6333 |
| **SentenceTransformers** | テキスト埋め込み | - |

---

## 🚀 セットアップ

### ステップ1: Ollamaコンテナ起動

```bash
# プロジェクトディレクトリに移動
cd /Users/koikedaisuke/MyProjects/データベース構築

# 全サービス起動（Ollama含む）
docker-compose up -d

# Ollama起動確認
docker ps | grep ollama

# Ollama接続テスト
curl http://localhost:11434/api/tags
```

### ステップ2: モデルダウンロード

Ollamaには多数のモデルがあります。最初に軽量モデルをダウンロード:

```bash
# 推奨: Llama 3.2 (3B) - バランス型
docker exec -it local_ollama ollama pull llama3.2

# 超軽量: Llama 3.2 1B - 最速
docker exec -it local_ollama ollama pull llama3.2:1b

# Google製: Gemma2 2B
docker exec -it local_ollama ollama pull gemma2:2b
```

**ダウンロード時間**: 約1-5分（モデルサイズによる）

### ステップ3: 依存関係インストール

```bash
# Python依存関係インストール
pip install -r requirements.txt

# または個別に
pip install langchain langchain-community ollama sentence-transformers streamlit streamlit-chat
```

### ステップ4: 動作確認

```bash
# モデル一覧確認
docker exec -it local_ollama ollama list

# 期待される出力:
# NAME              ID           SIZE      MODIFIED
# llama3.2:latest   a80c4f17acd5 2.0 GB    2 minutes ago
```

---

## 💻 使い方

### アプリケーション起動

#### 1. チャットアプリ

```bash
# チャットアプリ起動
streamlit run apps/rag/chat_app.py

# ブラウザで開く
# http://localhost:8501
```

**機能:**
- Ollamaとの会話
- ストリーミング応答
- 会話履歴保存（MongoDB）
- モデル切り替え

#### 2. RAGアプリ

```bash
# RAGアプリ起動
streamlit run apps/rag/rag_app.py

# ブラウザで開く
# http://localhost:8501
```

**機能:**
- ドキュメント追加
- 質問に関連ドキュメント検索
- 検索結果を元に回答生成
- 参考元表示

---

## 📱 アプリケーション

### 1. チャットアプリ (`chat_app.py`)

#### 基本的な使い方

1. **ブラウザで開く**: http://localhost:8501
2. **モデル選択**: サイドバーでモデルを選択
3. **メッセージ入力**: 下部の入力欄にメッセージ
4. **送信**: Enterキー

#### 特徴

- **ストリーミング応答**: リアルタイムで回答が表示される
- **会話履歴**: MongoDBに自動保存
- **セッション管理**: 会話ごとにセッションID付与
- **モデル切り替え**: 複数モデルを切り替え可能

#### スクリーンショット的な使い方

```
┌─────────────────────────────────────┐
│  サイドバー                         │
│  - モデル選択: llama3.2             │
│  - セッションID: session_20260311   │
│  - メッセージ数: 4                  │
│  - [🗑️ 会話をクリア]                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  メインエリア                       │
│                                     │
│  👤 User: こんにちは                │
│  🤖 Assistant: こんにちは！         │
│      どのようなお手伝いができますか？│
│                                     │
│  👤 User: Pythonについて教えて      │
│  🤖 Assistant: Pythonは...          │
│                                     │
│  [メッセージを入力...]              │
└─────────────────────────────────────┘
```

---

### 2. RAGアプリ (`rag_app.py`)

#### 基本的な使い方

1. **ドキュメント追加**
   - サイドバーの「ドキュメント追加」
   - テキスト入力
   - 「追加」ボタン

2. **質問**
   - チャットタブで質問入力
   - 自動で関連ドキュメント検索
   - 検索結果を元に回答生成

3. **検索テスト**
   - 「検索テスト」タブ
   - LLMを使わずドキュメント検索のみテスト

#### 使用例

**ステップ1: ドキュメント追加**

```
サイドバー > ドキュメント追加

テキスト:
「PostgreSQLは強力なオープンソースの
リレーショナルデータベースです。
pgvector拡張によりベクトル検索も可能です。」

タイトル: PostgreSQL概要

[📝 追加]
```

**ステップ2: 質問**

```
チャット入力:
「データベースでベクトル検索するには？」

→ 関連ドキュメント検索
→ PostgreSQL概要が見つかる
→ 回答生成:
「pgvector拡張を使うことで、PostgreSQLで
ベクトル検索ができます...」
```

#### 参考ドキュメント表示

回答の下に「📚 参考ドキュメント」が表示され:
- どのドキュメントを参照したか
- 類似度スコア
- ドキュメント内容

---

## 🔧 トラブルシューティング

### 問題1: Ollamaに接続できない

**症状:**
```
❌ Ollamaに接続できません
```

**原因**: Ollamaコンテナが起動していない

**解決:**
```bash
# コンテナ確認
docker ps | grep ollama

# 起動していなければ
docker-compose up -d ollama

# ログ確認
docker logs local_ollama
```

---

### 問題2: モデルがない

**症状:**
```
⚠️ モデルがインストールされていません
```

**原因**: モデルをダウンロードしていない

**解決:**
```bash
# モデルダウンロード
docker exec -it local_ollama ollama pull llama3.2

# 確認
docker exec -it local_ollama ollama list
```

---

### 問題3: 応答が遅い

**原因**: モデルが大きすぎる、またはメモリ不足

**解決:**

1. **軽量モデルに切り替え**
   ```bash
   docker exec -it local_ollama ollama pull llama3.2:1b
   ```

2. **Colimaメモリ増強**
   ```bash
   colima stop
   colima start --cpu 4 --memory 8
   ```

---

### 問題4: RAGで検索結果が出ない

**原因**: ドキュメントが追加されていない

**解決:**
1. サイドバーの「ドキュメント追加」
2. テキスト入力して追加
3. 統計で「ドキュメント数」を確認

---

### 問題5: Streamlitが起動しない

**症状:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**解決:**
```bash
pip install -r requirements.txt

# または
pip install streamlit streamlit-chat
```

---

## 🤖 推奨モデル

### モデル選択ガイド

| モデル | サイズ | 速度 | 品質 | 推奨用途 |
|--------|--------|------|------|----------|
| **llama3.2:1b** | 1B | ⚡⚡⚡ | ⭐⭐ | 高速チャット |
| **llama3.2** (3B) | 3B | ⚡⚡ | ⭐⭐⭐ | バランス型（推奨） |
| **gemma2:2b** | 2B | ⚡⚡⚡ | ⭐⭐⭐ | Google製 |
| **llama3.2:7b** | 7B | ⚡ | ⭐⭐⭐⭐ | 高品質（要メモリ） |
| **phi3** | 3.8B | ⚡⚡ | ⭐⭐⭐ | Microsoft製 |

### ダウンロード方法

```bash
# Llama 3.2 (3B) - 推奨
docker exec -it local_ollama ollama pull llama3.2

# Llama 3.2 (1B) - 超軽量
docker exec -it local_ollama ollama pull llama3.2:1b

# Gemma2 (2B) - Google製
docker exec -it local_ollama ollama pull gemma2:2b

# Llama 3.2 (7B) - 高品質（メモリ8GB以上推奨）
docker exec -it local_ollama ollama pull llama3.2:7b

# Phi3 (3.8B) - Microsoft製
docker exec -it local_ollama ollama pull phi3
```

### システム要件

| モデルサイズ | 推奨メモリ | Colimaメモリ設定 |
|------------|----------|----------------|
| 1B-2B | 4GB | `--memory 4` |
| 3B-4B | 6GB | `--memory 6` |
| 7B-8B | 8GB以上 | `--memory 8` |

---

## 📚 応用例

### 例1: プロジェクトドキュメントのQA

**ユースケース**: プロジェクトのREADMEやドキュメントを学習させて質問応答

```python
# RAGアプリで実施
1. README.mdの内容をコピペして追加
2. SETUP_GUIDE.mdの内容を追加
3. 質問: "このプロジェクトのセットアップ方法は？"
```

### 例2: コードレビュー補助

**ユースケース**: コードを渡して問題点を指摘してもらう

```python
# チャットアプリで実施
質問: "以下のコードをレビューしてください"
[コードを貼り付け]
```

### 例3: 日本語⇔英語翻訳

```python
質問: "以下の日本語を英語に翻訳してください: データベース構築"
```

---

## 🎓 ベストプラクティス

### チャットアプリ

1. **明確な質問** - 具体的に聞く
2. **文脈を提供** - 背景情報を含める
3. **会話履歴活用** - 前の会話を参照できる

### RAGアプリ

1. **ドキュメント整理** - 関連情報をまとめて追加
2. **適切な粒度** - 長すぎず短すぎないチャンク
3. **検索テスト** - まず検索テストで確認

---

## 🔒 プライバシー・セキュリティ

### データの保存場所

- **会話履歴**: MongoDB (ローカル)
- **ドキュメント**: Qdrant (ローカル)
- **モデル**: Docker Volume (ローカル)

### 外部通信

- ❌ **なし** - 全てローカルで完結
- ❌ **APIキー不要**
- ❌ **インターネット不要**（モデルDL後）

---

## 📊 パフォーマンス最適化

### メモリ使用量削減

```bash
# 軽量モデル使用
docker exec -it local_ollama ollama pull llama3.2:1b

# 未使用モデル削除
docker exec -it local_ollama ollama rm <model_name>
```

### 速度向上

1. **Colimaリソース増強**
   ```bash
   colima stop
   colima start --cpu 6 --memory 12
   ```

2. **軽量モデル使用**
   - llama3.2:1b (最速)

3. **ドキュメント数削減**
   - RAGで検索するドキュメント数を減らす

---

## 🔗 関連ドキュメント

- **[README.md](./README.md)** - プロジェクト概要
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - セットアップ
- **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** - Docker操作
- **[MULTI_APP_GUIDE.md](./MULTI_APP_GUIDE.md)** - 複数アプリ管理

---

## 📝 更新履歴

### 2026-03-11
- 初版作成
- Ollama + Streamlit統合
- チャットアプリ、RAGアプリ実装

---

**作成者**: Claude Sonnet 4.5 (Anthropic)
**最終更新**: 2026年3月11日
**バージョン**: 1.0

🤖 **完全ローカル・完全プライベートなAIシステムをお楽しみください！**
