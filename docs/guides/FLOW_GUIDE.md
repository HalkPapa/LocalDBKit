# システム使用フロー完全ガイド

インターフェースから各サーバーへの接続フローを詳細解説

**作成日**: 2026年3月15日
**バージョン**: 1.0.0
**関連図**: [flow.drawio](flow.drawio)

---

## 📋 目次

1. [フロー1: LLMチャット（RAG統合）](#フロー1-llmチャットrag統合)
2. [フロー2: 知識追加](#フロー2-知識追加)
3. [フロー3: データベース管理](#フロー3-データベース管理)
4. [フロー4: 学習管理・可視化](#フロー4-学習管理可視化)
5. [フロー5: RAG API直接利用](#フロー5-rag-api直接利用)
6. [エラーハンドリング](#エラーハンドリング)
7. [パフォーマンス最適化](#パフォーマンス最適化)

---

## フロー1: LLMチャット（RAG統合）

### 概要

ユーザーがOpen WebUIで質問すると、RAGシステムが知識ベースを検索し、関連情報を含めてLLMが回答を生成します。

### フロー図

```
┌──────┐  1.質問   ┌─────────┐  2.知識検索  ┌────────┐  3.ベクトル検索  ┌────────┐
│ユーザー│ ────────> │Open WebUI│ ──────────> │RAG API │ ──────────────> │ Qdrant │
└──────┘           └─────────┘             └────────┘                └────────┘
   ↑ 10.回答           │                       ↑                        │
   │                  │ 6.プロンプト           │ 5.コンテキスト          │ 4.関連知識
   │                  ↓   +コンテキスト        └────────────────────────┘
   │               ┌────────┐  7.LLM応答
   │               │ Ollama │ ──────────┐
   │               └────────┘           ↓
   │                                 ┌─────────┐  8.履歴保存  ┌─────────┐
   └─────────────────────────────────│Open WebUI│ ──────────> │ MongoDB │
                                     └─────────┘             └─────────┘
                                                                  │ 9.セッション記録
                                                                  ↓
                                                            ┌──────────────┐
                                                            │learning_     │
                                                            │tracker.py    │
                                                            └──────────────┘
```

### ステップ詳細

#### ステップ1: ユーザーが質問入力

**UI**: Open WebUI (http://localhost:3000)

```
ユーザー入力例:
"Pythonのリスト内包表記について教えて"
```

#### ステップ2: 知識検索リクエスト

**通信**: Open WebUI → RAG API

```http
POST http://localhost:8003/search
Content-Type: application/json

{
  "query": "Pythonのリスト内包表記について教えて",
  "top_k": 3
}
```

**処理内容**:
- `openwebui_rag_function.py` の `pipe()` メソッドが自動実行
- ユーザーメッセージを検索クエリとして抽出

#### ステップ3: ベクトル検索

**通信**: RAG API → Qdrant

```python
# rag_api.py内部処理
query_vector = embedder.encode(query).tolist()  # ベクトル化

results = client.query_points(
    collection_name="knowledge",
    query=query_vector,
    limit=top_k,
    with_payload=True
)
```

**Qdrant内部処理**:
- コサイン類似度計算
- スコアの高い順にチャンクを取得

#### ステップ4: 関連知識返却

**通信**: Qdrant → RAG API (レスポンス)

```json
[
  {
    "text": "Pythonのリスト内包表記は、ループより高速で読みやすい...",
    "score": 0.89,
    "filename": "sample_python.md",
    "chunk_index": 3
  },
  {
    "text": "リスト内包表記の例: squared = [x**2 for x in range(10)]",
    "score": 0.85,
    "filename": "sample_python.md",
    "chunk_index": 4
  }
]
```

#### ステップ5: コンテキスト生成

**処理**: RAG API内部

```python
context = f"""
[知識ベースからの参照情報]

【参照 1】(sample_python.md)
Pythonのリスト内包表記は、ループより高速で読みやすい...

【参照 2】(sample_python.md)
リスト内包表記の例: squared = [x**2 for x in range(10)]

上記の知識を参考にして、正確に回答してください。
知識に記載されていない内容は推測せず、「知識ベースにありません」と答えてください。
"""
```

#### ステップ6: LLMプロンプト生成

**通信**: Open WebUI → Ollama

```json
{
  "model": "gemma2:9b",
  "messages": [
    {
      "role": "system",
      "content": "[知識ベースからの参照情報]\n\n【参照 1】..."
    },
    {
      "role": "user",
      "content": "Pythonのリスト内包表記について教えて"
    }
  ]
}
```

**Ollama処理**:
- モデルロード (初回のみ)
- トークン生成
- ストリーミングレスポンス

#### ステップ7: LLM応答

**通信**: Ollama → Open WebUI (ストリーミング)

```
Pythonのリスト内包表記は、ループより高速で読みやすい構文です。

例:
squared = [x**2 for x in range(10)]

これは以下のループと同等です:
squared = []
for x in range(10):
    squared.append(x**2)

知識ベースによると、リスト内包表記を使うことがベストプラクティスとされています。
```

#### ステップ8: 履歴保存

**通信**: Open WebUI → MongoDB

```javascript
// sessionsコレクションに保存
{
  "session_id": "uuid-12345",
  "user_id": "user-001",
  "timestamp": "2026-03-15T10:30:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Pythonのリスト内包表記について教えて"
    },
    {
      "role": "assistant",
      "content": "Pythonのリスト内包表記は...",
      "sources": ["sample_python.md"]
    }
  ]
}
```

#### ステップ9: セッション記録

**処理**: learning_tracker.py

```python
tracker.record_session({
    "id": "uuid-12345",
    "title": "Pythonリスト内包表記について",
    "start_time": "2026-03-15T10:30:00",
    "model": "gemma2:9b",
    "messages": [...],
    "topic": "Python"
})
```

**MongoDB保存内容**:
```javascript
// sessionsコレクション
{
  "session_id": "uuid-12345",
  "title": "Pythonリスト内包表記について",
  "start_time": ISODate("2026-03-15T10:30:00Z"),
  "model_used": "gemma2:9b",
  "messages_count": 2,
  "topic": "Python",
  "duration_seconds": 15
}

// messagesコレクション
{
  "session_id": "uuid-12345",
  "timestamp": ISODate("2026-03-15T10:30:00Z"),
  "role": "user",
  "content": "Pythonのリスト内包表記について教えて",
  "topic": "Python"
}
```

#### ステップ10: 回答表示

**UI**: Open WebUI

- マークダウンレンダリング
- コードシンタックスハイライト
- 参照ソース表示（オプション）

### 使用例

```bash
# 1. システム起動
docker-compose up -d

# 2. Open WebUI起動確認
curl http://localhost:3000

# 3. ブラウザでアクセス
open http://localhost:3000

# 4. 初回: アカウント作成
# Email: user@example.com
# Password: ********

# 5. チャット開始
# 「Pythonのリスト内包表記について教えて」と入力
```

### パフォーマンス

| 処理 | 所要時間 |
|------|---------|
| ベクトル検索 (Qdrant) | 10-50ms |
| コンテキスト生成 | 5-10ms |
| LLM推論 (Gemma2:9b) | 2-5秒 (初回: ~10秒) |
| MongoDB保存 | 10-20ms |
| **合計** | **2-5秒** |

---

## フロー2: 知識追加

### 概要

ドキュメント（PDF/Markdown/Text/HTML）を知識ベースに追加するフローです。

### フロー図

```
┌──────┐  1.ドキュメント  ┌──────────────┐  2.処理実行  ┌──────────────┐  3.ベクトル保存  ┌────────┐
│ユーザー│ ─────────────> │add_knowledge │ ──────────> │rag_system.py │ ──────────────> │ Qdrant │
└──────┘  .pdf/.md/.txt   │.sh           │             │              │                └────────┘
   ↑                      └──────────────┘             └──────────────┘                     │
   │                                                                                        │
   └────────────────────────── 4.完了通知 ─────────────────────────────────────────────────┘
```

### ステップ詳細

#### ステップ1: ドキュメント指定

**方法A: 個別ファイル**
```bash
./scripts/knowledge/add_knowledge.sh ~/Documents/python_guide.pdf
```

**方法B: 複数ファイル**
```bash
./scripts/knowledge/add_knowledge.sh ~/Documents/*.md
```

**方法C: フォルダ一括**
```bash
./scripts/knowledge/add_knowledge.sh ~/Documents/programming/
```

**サポート形式**:
- PDF (`.pdf`)
- Markdown (`.md`)
- Text (`.txt`)
- HTML (`.html`)

#### ステップ2: スクリプト実行

**処理内容** (`add_knowledge.sh`):

```bash
for item in "$@"; do
    if [ -f "$item" ]; then
        # ファイルの場合
        echo "📄 追加: $item"
        python3 rag_system.py add "$item"
    elif [ -d "$item" ]; then
        # フォルダの場合
        echo "📁 フォルダ: $item"
        find "$item" -type f \( -name "*.pdf" -o -name "*.md" -o -name "*.txt" \) | while read file; do
            echo "📄 追加: $file"
            python3 rag_system.py add "$file"
        done
    fi
done
```

#### ステップ3: rag_system.py処理

**処理フロー**:

1. **ファイル読み込み**
```python
if file_path.endswith('.pdf'):
    text = extract_text_from_pdf(file_path)
elif file_path.endswith('.md') or file_path.endswith('.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
elif file_path.endswith('.html'):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
```

2. **チャンク分割**
```python
chunk_size = 500      # 500文字
chunk_overlap = 100   # 100文字オーバーラップ

chunks = []
for i in range(0, len(text), chunk_size - chunk_overlap):
    chunk = text[i:i + chunk_size]
    chunks.append(chunk)
```

**例**:
```
元テキスト (1500文字)
↓
チャンク1: 0-500文字
チャンク2: 400-900文字   (100文字オーバーラップ)
チャンク3: 800-1300文字
チャンク4: 1200-1500文字
```

3. **ベクトル化**
```python
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer('all-MiniLM-L6-v2')
vectors = embedder.encode(chunks)  # 384次元ベクトル
```

4. **Qdrant保存**
```python
from qdrant_client.models import PointStruct

points = []
for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
    points.append(PointStruct(
        id=uuid.uuid4().hex,
        vector=vector.tolist(),
        payload={
            "chunk_text": chunk,
            "filename": filename,
            "chunk_index": idx,
            "file_type": file_type,
            "added_at": datetime.now().isoformat()
        }
    ))

client.upsert(collection_name="knowledge", points=points)
```

#### ステップ4: 完了通知

**出力例**:
```
📚 知識追加ツール
==================================================
📄 追加: /path/to/documents/python_guide.pdf
   ├─ ファイルサイズ: 2.3MB
   ├─ 抽出テキスト: 45,230文字
   ├─ チャンク数: 113
   └─ ベクトル保存: 完了

✅ 完了

📊 現在の知識ベース:
┌────────────────────────┬──────┬──────────────────┐
│ ファイル名             │ 数   │ 追加日時         │
├────────────────────────┼──────┼──────────────────┤
│ python_guide.pdf       │  113 │ 2026-03-15 10:30 │
│ sample_python.md       │   15 │ 2026-03-14 15:20 │
└────────────────────────┴──────┴──────────────────┘
合計: 128チャンク
```

### 使用例

**例1: プログラミング書籍を追加**
```bash
./scripts/knowledge/add_knowledge.sh ~/Books/effective_python.pdf
```

**例2: 個人ノートを一括追加**
```bash
./scripts/knowledge/add_knowledge.sh ~/Notes/programming/*.md
```

**例3: プロジェクトドキュメント追加**
```bash
./scripts/knowledge/add_knowledge.sh ~/Projects/myapp/docs/
```

**例4: Webページを追加**
```bash
# Webページをダウンロード
curl https://docs.python.org/3/tutorial/ > python_tutorial.html

# 知識ベースに追加
./scripts/knowledge/add_knowledge.sh python_tutorial.html
```

### API経由での追加

```bash
curl -X POST http://localhost:8003/documents/add \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.pdf",
    "metadata": {
      "category": "programming",
      "language": "ja",
      "author": "Example Author"
    }
  }'
```

**レスポンス**:
```json
{
  "status": "success",
  "file_path": "/path/to/document.pdf",
  "chunks_added": 113
}
```

### 知識の確認

```bash
# 一覧表示
python3 rag_system.py list

# 検索テスト
python3 rag_system.py search "Pythonのリスト操作"
```

---

## フロー3: データベース管理

### 概要

Web UIを使用してPostgreSQLとMongoDBを管理します。

### PostgreSQL管理フロー

```
┌──────┐  ブラウザアクセス  ┌─────────┐  SQL実行  ┌────────────┐
│ユーザー│ ────────────────> │ Adminer │ ────────> │ PostgreSQL │
└──────┘  :8080             └─────────┘          └────────────┘
                               ↑                       │
                               └───── クエリ結果 ──────┘
```

#### ステップ1: Adminerアクセス

**URL**: http://localhost:8080

**ログイン情報**:
```
システム: PostgreSQL
サーバー: postgres (コンテナ名)
ユーザー名: postgres
パスワード: password
データベース: postgres
```

#### ステップ2: SQL実行

**テーブル作成例**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**ベクトル検索テーブル例**:
```sql
-- pgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- ベクトル検索テーブル
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    text TEXT,
    embedding vector(384),  -- 384次元ベクトル
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ベクトルインデックス作成
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- ベクトル検索
SELECT text, 1 - (embedding <=> '[0.1, 0.2, ...]') AS similarity
FROM embeddings
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

**データ挿入**:
```sql
INSERT INTO users (name, email) VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com');
```

**データ取得**:
```sql
SELECT * FROM users WHERE email LIKE '%example.com';
```

#### Adminer機能

- **テーブル一覧**: 構造確認、行数表示
- **SQL実行**: カスタムクエリ
- **データ編集**: GUI編集
- **エクスポート**: CSV/SQL形式
- **インポート**: SQL/CSVファイル

### MongoDB管理フロー

```
┌──────┐  ブラウザアクセス  ┌──────────────┐  CRUD操作  ┌─────────┐
│ユーザー│ ────────────────> │Mongo Express │ ─────────> │ MongoDB │
└──────┘  :8081             └──────────────┘           └─────────┘
                               ↑                           │
                               └───── ドキュメント取得 ─────┘
```

#### ステップ1: Mongo Expressアクセス

**URL**: http://localhost:8081

**ログイン情報**:
```
Username: admin
Password: password
```

#### ステップ2: データベース操作

**コレクション作成**:
```javascript
// learning_dbデータベース内
db.createCollection("sessions")
db.createCollection("messages")
db.createCollection("goals")
```

**ドキュメント挿入**:
```javascript
db.sessions.insertOne({
  session_id: "uuid-12345",
  title: "Pythonプログラミング学習",
  start_time: new Date("2026-03-15T10:30:00Z"),
  model_used: "gemma2:9b",
  messages_count: 10,
  topic: "Python"
})
```

**クエリ実行**:
```javascript
// トピック別集計
db.sessions.aggregate([
  { $group: { _id: "$topic", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// 期間指定検索
db.sessions.find({
  start_time: {
    $gte: new Date("2026-03-01"),
    $lt: new Date("2026-04-01")
  }
})
```

**ドキュメント更新**:
```javascript
db.sessions.updateOne(
  { session_id: "uuid-12345" },
  { $set: { end_time: new Date(), duration_seconds: 600 } }
)
```

**削除**:
```javascript
db.sessions.deleteOne({ session_id: "uuid-12345" })
```

#### Mongo Express機能

- **データベース一覧**: サイズ確認
- **コレクション管理**: 作成/削除
- **ドキュメント編集**: JSON編集
- **クエリ実行**: MongoDB Shell風
- **エクスポート**: JSON/CSV

### CLI操作

**PostgreSQL CLI**:
```bash
docker exec -it local_postgres psql -U postgres

# テーブル一覧
\dt

# クエリ実行
SELECT * FROM users;

# 終了
\q
```

**MongoDB CLI**:
```bash
docker exec -it local_mongodb mongosh -u admin -p password

# データベース一覧
show dbs

# データベース選択
use learning_db

# コレクション一覧
show collections

# ドキュメント取得
db.sessions.find().pretty()

# 終了
exit
```

**Redis CLI**:
```bash
docker exec -it local_redis redis-cli

# キー一覧
KEYS *

# 値取得
GET mykey

# 値設定
SET mykey "value"

# TTL設定
SETEX mykey 3600 "expires in 1 hour"

# 終了
exit
```

---

## フロー4: 学習管理・可視化

### 概要

MongoDBに保存された学習データをStreamlitダッシュボードで可視化します。

### フロー図

```
┌──────┐  ブラウザアクセス  ┌──────────────────┐  データ取得  ┌─────────┐
│ユーザー│ ────────────────> │learning_dashboard│ ──────────> │ MongoDB │
└──────┘  :8502             │.py (Streamlit)   │            │learning_db
                            └──────────────────┘            │- sessions
                                    ↑                       │- messages
                                    │                       │- goals
                                    └────── 統計計算 ────────┘

┌──────┐  モデル評価表示  ┌──────────────────┐
│ユーザー│ ──────────────> │llm_dashboard.py  │
└──────┘  :8501           │(Streamlit)       │
                          └──────────────────┘
```

### 学習管理ダッシュボード (:8502)

#### アクセス

```bash
# ダッシュボード起動
streamlit run learning_dashboard.py --server.port 8502

# ブラウザで開く
open http://localhost:8502
```

#### 表示内容

**1. 学習統計サマリー**
```
┌─────────────────────────────────────┐
│ 📊 学習統計サマリー                  │
├─────────────────────────────────────┤
│ 総学習時間:     12時間30分           │
│ セッション数:   45セッション         │
│ 総メッセージ数: 320メッセージ        │
│ 平均セッション: 16.7分               │
└─────────────────────────────────────┘
```

**2. 日別学習時間グラフ**
```python
import streamlit as st
import pandas as pd
import plotly.express as px

# MongoDB からデータ取得
sessions = tracker.get_sessions_by_date_range(
    start_date=datetime(2026, 3, 1),
    end_date=datetime(2026, 3, 15)
)

# 日別集計
df = pd.DataFrame([
    {
        'date': s['start_time'].date(),
        'duration': s['duration_seconds'] / 60  # 分に変換
    }
    for s in sessions
])

daily = df.groupby('date')['duration'].sum().reset_index()

# グラフ表示
fig = px.bar(daily, x='date', y='duration', title='日別学習時間')
st.plotly_chart(fig)
```

**3. トピック分布**
```python
# トピック別集計
topics = tracker.get_topic_distribution()

# 円グラフ
fig = px.pie(
    values=list(topics.values()),
    names=list(topics.keys()),
    title='学習トピック分布'
)
st.plotly_chart(fig)
```

**出力例**:
```
Python:     40%
JavaScript: 25%
Docker:     20%
SQL:        15%
```

**4. 目標管理**
```python
# 目標一覧
goals = tracker.get_goals()

for goal in goals:
    st.subheader(goal['title'])
    progress = goal['current'] / goal['target'] * 100
    st.progress(progress / 100)
    st.write(f"{goal['current']} / {goal['target']} {goal['unit']} ({progress:.1f}%)")
```

**表示例**:
```
■ Python基礎マスター
  ████████░░ 80%
  40 / 50 セッション

■ 毎日1時間学習
  ███████░░░ 70%
  10 / 14 日達成
```

**5. 週次レポート**
```python
# 今週の統計
this_week = tracker.get_weekly_stats()

st.write(f"""
### 今週の学習 (3/10 - 3/16)
- 学習時間: {this_week['total_hours']}時間
- セッション数: {this_week['session_count']}回
- 主なトピック: {', '.join(this_week['top_topics'])}
- 達成した目標: {this_week['goals_completed']}個
""")
```

### モデル評価ダッシュボード (:8501)

#### アクセス

```bash
streamlit run llm_dashboard.py --server.port 8501
open http://localhost:8501
```

#### 表示内容

**1. モデル比較表**
```
┌────────────┬──────────┬───────────┬────────┬──────┐
│ モデル     │ 日本語   │ ペルソナ  │ 総合   │ サイズ│
├────────────┼──────────┼───────────┼────────┼──────┤
│ Gemma2:9b  │ 66.7%    │ 91.7%     │ 79.2%  │ 5.4GB│
│ Qwen2.5:7b │ 44.4%    │ 100%      │ 72.2%  │ 4.7GB│
└────────────┴──────────┴───────────┴────────┴──────┘
```

**2. 性能グラフ**
```python
import plotly.graph_objects as go

fig = go.Figure(data=[
    go.Bar(name='Gemma2:9b', x=['日本語', 'ペルソナ', '総合'], y=[66.7, 91.7, 79.2]),
    go.Bar(name='Qwen2.5:7b', x=['日本語', 'ペルソナ', '総合'], y=[44.4, 100, 72.2])
])

fig.update_layout(barmode='group', title='モデル性能比較')
st.plotly_chart(fig)
```

**3. 詳細テスト結果**
```python
# テスト結果表示
results = load_evaluation_results()

for model, tests in results.items():
    st.subheader(model)

    for test in tests:
        with st.expander(f"{test['category']} - {test['question']}"):
            st.write("**回答:**")
            st.write(test['response'])
            st.write(f"**スコア:** {test['score']}/5")
            st.write(f"**評価:** {test['evaluation']}")
```

---

## フロー5: RAG API直接利用

### 概要

外部アプリケーションからRAG APIを直接呼び出して知識検索を行います。

### フロー図

```
┌──────────┐  HTTP Request   ┌─────────┐  ベクトル検索  ┌────────┐
│外部アプリ │ ──────────────> │ RAG API │ ────────────> │ Qdrant │
│カスタムUI│                 │  :8003  │               └────────┘
└──────────┘                 └─────────┘                    │
     ↑                           │                          │
     └────── JSON Response ──────┘                          │
            (知識データ)          │                          │
                                 └────── クエリ実行 ─────────┘
```

### エンドポイント一覧

#### 1. POST /search - 知識検索

**リクエスト**:
```bash
curl -X POST http://localhost:8003/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Pythonのリスト操作",
    "top_k": 5
  }'
```

**レスポンス**:
```json
[
  {
    "text": "Pythonのリストは、順序付きで変更可能なコレクションです...",
    "score": 0.89,
    "filename": "sample_python.md",
    "chunk_index": 2,
    "metadata": {
      "file_type": "markdown",
      "added_at": "2026-03-15T10:00:00Z"
    }
  },
  {
    "text": "リスト内包表記を使うことで、ループより高速...",
    "score": 0.85,
    "filename": "sample_python.md",
    "chunk_index": 4,
    "metadata": {...}
  }
]
```

#### 2. GET /documents - ドキュメント一覧

**リクエスト**:
```bash
curl http://localhost:8003/documents
```

**レスポンス**:
```json
{
  "documents": [
    {
      "filename": "sample_python.md",
      "chunks": 15,
      "added_at": "2026-03-15T10:00:00Z"
    },
    {
      "filename": "python_guide.pdf",
      "chunks": 113,
      "added_at": "2026-03-15T11:30:00Z"
    }
  ],
  "total_chunks": 128
}
```

#### 3. POST /documents/add - ドキュメント追加

**リクエスト**:
```bash
curl -X POST http://localhost:8003/documents/add \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.pdf",
    "metadata": {
      "category": "programming",
      "language": "ja"
    }
  }'
```

**レスポンス**:
```json
{
  "status": "success",
  "file_path": "/path/to/document.pdf",
  "chunks_added": 113
}
```

#### 4. DELETE /documents/delete - ドキュメント削除

**リクエスト**:
```bash
curl -X DELETE http://localhost:8003/documents/delete \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "old_document.pdf"
  }'
```

**レスポンス**:
```json
{
  "status": "success",
  "filename": "old_document.pdf",
  "chunks_deleted": 95
}
```

#### 5. POST /context - LLM用コンテキスト生成

**リクエスト**:
```bash
curl -X POST http://localhost:8003/context \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Pythonのリスト操作",
    "top_k": 3
  }'
```

**レスポンス**:
```json
{
  "context": "[知識ベースからの参照情報]\n\n【参照 1】(sample_python.md)\nPythonのリストは...\n\n【参照 2】(sample_python.md)\nリスト内包表記...\n\n上記の知識を参考にして、正確に回答してください。",
  "query": "Pythonのリスト操作"
}
```

#### 6. GET /health - ヘルスチェック

**リクエスト**:
```bash
curl http://localhost:8003/health
```

**レスポンス**:
```json
{
  "status": "healthy"
}
```

### API Docs

Swagger UI で全エンドポイントを確認:
```bash
open http://localhost:8003/docs
```

### 使用例

#### Python SDKでの利用

```python
import requests

class RAGClient:
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url

    def search(self, query, top_k=3):
        """知識検索"""
        response = requests.post(
            f"{self.base_url}/search",
            json={"query": query, "top_k": top_k}
        )
        return response.json()

    def add_document(self, file_path, metadata=None):
        """ドキュメント追加"""
        response = requests.post(
            f"{self.base_url}/documents/add",
            json={"file_path": file_path, "metadata": metadata}
        )
        return response.json()

# 使用例
client = RAGClient()

# 知識検索
results = client.search("Pythonのリスト操作")
for r in results:
    print(f"[{r['score']:.2f}] {r['text'][:100]}...")

# ドキュメント追加
client.add_document(
    "/path/to/document.pdf",
    metadata={"category": "programming"}
)
```

#### JavaScriptでの利用

```javascript
class RAGClient {
  constructor(baseURL = 'http://localhost:8003') {
    this.baseURL = baseURL;
  }

  async search(query, topK = 3) {
    const response = await fetch(`${this.baseURL}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK })
    });
    return response.json();
  }

  async addDocument(filePath, metadata = {}) {
    const response = await fetch(`${this.baseURL}/documents/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath, metadata })
    });
    return response.json();
  }
}

// 使用例
const client = new RAGClient();

// 知識検索
const results = await client.search('Pythonのリスト操作');
results.forEach(r => {
  console.log(`[${r.score.toFixed(2)}] ${r.text.substring(0, 100)}...`);
});

// ドキュメント追加
await client.addDocument('/path/to/document.pdf', {
  category: 'programming'
});
```

---

## エラーハンドリング

### よくあるエラーと対処法

#### 1. RAG API接続エラー

**エラー**:
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**原因**: RAG APIが起動していない

**対処法**:
```bash
# APIサーバー起動確認
docker-compose ps rag-api

# 起動していない場合
python3 rag_api.py

# または
docker-compose restart
```

#### 2. Qdrant接続エラー

**エラー**:
```
qdrant_client.exceptions.UnexpectedResponse: Unexpected Response: 404
```

**原因**: コレクションが存在しない

**対処法**:
```bash
# コレクション作成
python3 rag_system.py init

# または手動作成
curl -X PUT http://localhost:6333/collections/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'
```

#### 3. MongoDB接続エラー

**エラー**:
```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 61] Connection refused
```

**原因**: MongoDBが起動していない

**対処法**:
```bash
# コンテナ状態確認
docker-compose ps

# 再起動
docker-compose restart mongodb
```

#### 4. Ollama モデルロードエラー

**エラー**:
```
Error: model 'gemma2:9b' not found
```

**原因**: モデルがダウンロードされていない

**対処法**:
```bash
docker exec -it local_ollama ollama pull gemma2:9b
```

#### 5. メモリ不足エラー

**エラー**:
```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**原因**: メモリ不足

**対処法**:
```bash
# Colima メモリ増加
colima stop
colima start --memory 16

# または小さいモデルを使用
docker exec -it local_ollama ollama pull gemma2:2b
```

---

## パフォーマンス最適化

### ベクトル検索最適化

#### インデックス作成

```python
# Qdrantのインデックス最適化
from qdrant_client.models import VectorParams, Distance

client.recreate_collection(
    collection_name="knowledge",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE,
        hnsw_config={
            "m": 16,              # 接続数（デフォルト: 16）
            "ef_construct": 100   # 構築時の探索範囲（デフォルト: 100）
        }
    )
)
```

**検索時の最適化**:
```python
results = client.query_points(
    collection_name="knowledge",
    query=query_vector,
    limit=top_k,
    with_payload=True,
    search_params={
        "hnsw_ef": 128,  # 検索時の探索範囲（大きいほど精度↑速度↓）
        "exact": False   # 近似検索使用
    }
)
```

### LLM推論最適化

#### コンテキスト長の調整

```python
# 長すぎるコンテキストは避ける
MAX_CONTEXT_LENGTH = 2000  # トークン数

context = generate_context(query, top_k=3)
if len(context) > MAX_CONTEXT_LENGTH:
    context = context[:MAX_CONTEXT_LENGTH]
```

#### ストリーミングレスポンス

```python
# Ollamaでストリーミング使用
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma2:9b",
        "prompt": prompt,
        "stream": True  # ストリーミング有効
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk['response'], end='', flush=True)
```

### データベースクエリ最適化

#### MongoDB インデックス

```javascript
// セッション検索用インデックス
db.sessions.createIndex({ "start_time": -1 })
db.sessions.createIndex({ "topic": 1 })
db.sessions.createIndex({ "user_id": 1, "start_time": -1 })

// メッセージ検索用インデックス
db.messages.createIndex({ "session_id": 1, "timestamp": -1 })
```

#### PostgreSQL インデックス

```sql
-- 複合インデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_embeddings_created ON embeddings(created_at DESC);

-- ベクトル検索インデックス
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
```

### キャッシング戦略

#### Redis キャッシュ

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def search_with_cache(query, top_k=3):
    # キャッシュキー生成
    cache_key = f"search:{query}:{top_k}"

    # キャッシュチェック
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # RAG検索実行
    results = rag.search(query, top_k=top_k)

    # キャッシュ保存 (1時間)
    r.setex(cache_key, 3600, json.dumps(results))

    return results
```

### バッチ処理

#### 複数ドキュメントの一括追加

```python
def batch_add_documents(file_paths, batch_size=10):
    """バッチでドキュメント追加"""
    all_points = []

    for file_path in file_paths:
        chunks = process_document(file_path)
        vectors = embedder.encode(chunks)

        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            all_points.append(PointStruct(...))

        # バッチサイズに達したらアップロード
        if len(all_points) >= batch_size:
            client.upsert(collection_name="knowledge", points=all_points)
            all_points = []

    # 残りをアップロード
    if all_points:
        client.upsert(collection_name="knowledge", points=all_points)
```

### モニタリング

#### パフォーマンス計測

```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}: {(end - start) * 1000:.2f}ms")
        return result
    return wrapper

@measure_time
def search_knowledge(query):
    return rag.search(query)
```

**出力例**:
```
search_knowledge: 45.23ms
  ├─ vectorize: 12.34ms
  ├─ qdrant_search: 28.56ms
  └─ format_results: 4.33ms
```

---

## まとめ

### 主要フロー一覧

| フロー | 開始点 | 終了点 | 所要時間 |
|--------|--------|--------|----------|
| LLMチャット | Open WebUI | ユーザー | 2-5秒 |
| 知識追加 | add_knowledge.sh | Qdrant | 1-10秒/ドキュメント |
| DB管理 | Adminer/Mongo Express | PostgreSQL/MongoDB | 即時 |
| 学習可視化 | Dashboard | MongoDB | 即時 |
| API利用 | 外部アプリ | RAG API | 10-100ms |

### ポート一覧

| サービス | ポート | 用途 |
|---------|--------|------|
| Open WebUI | 3000 | LLMチャット |
| RAG API | 8003 | 知識検索API |
| Adminer | 8080 | PostgreSQL管理 |
| Mongo Express | 8081 | MongoDB管理 |
| LLM Dashboard | 8501 | モデル評価 |
| Learning Dashboard | 8502 | 学習管理 |
| PostgreSQL | 5432 | RDBMS |
| MongoDB | 27017 | NoSQL |
| Redis | 6379 | KVS |
| Qdrant | 6333 | Vector DB |
| Ollama | 11434 | LLMエンジン |

### 次のステップ

1. **実際に使ってみる**: Open WebUIでチャット開始
2. **知識を追加**: ドキュメントを知識ベースに追加
3. **学習を記録**: 学習目標を設定してダッシュボードで進捗確認
4. **カスタマイズ**: 外部アプリからRAG APIを利用

---

**作成者**: Claude Sonnet 4.5 (Anthropic)
**最終更新**: 2026年3月15日
**関連ドキュメント**:
- [ARCHITECTURE.md](ARCHITECTURE.md) - システムアーキテクチャ
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - プロジェクト全体サマリー
- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker操作ガイド
