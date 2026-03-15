# LocalDBKit スクリーンショット

このページでは、LocalDBKitの主要な機能とUIのスクリーンショットを紹介します。

## 📊 ダッシュボード

### Grafana監視ダッシュボード
**URL**: http://localhost:3001

モニタリングダッシュボードでは以下を確認できます：
- PostgreSQL、MongoDB、Redisのメトリクス
- リアルタイムパフォーマンス
- リソース使用状況
- クエリ実行時間

**ログイン情報**:
- Username: `admin`
- Password: `admin`

---

### Qdrantダッシュボード
**URL**: http://localhost:6333/dashboard

ベクトルデータベースの管理画面：
- コレクション一覧
- ベクトル検索
- インデックス状態
- ストレージ使用量

---

### Open WebUI
**URL**: http://localhost:3000

LLMチャットインターフェース：
- Ollamaとの対話
- RAG機能（ドキュメント検索）
- 会話履歴
- プロンプトテンプレート

---

## 🗄️ データベース管理UI

### Adminer (PostgreSQL)
**URL**: http://localhost:8080

PostgreSQLデータベース管理：
- テーブル閲覧・編集
- SQLクエリ実行
- データインポート/エクスポート
- スキーマ管理

**接続情報**:
- System: `PostgreSQL`
- Server: `postgres`
- Username: `postgres`
- Password: `postgres`
- Database: `mydb`

---

### Mongo Express (MongoDB)
**URL**: http://localhost:8081

MongoDB管理画面：
- データベース一覧
- コレクション管理
- ドキュメント編集
- クエリ実行

---

## 📈 分析ダッシュボード

### LLMダッシュボード
**URL**: http://localhost:8501

LLMモデル評価ダッシュボード：
- モデル性能比較
- 日本語能力評価
- ペルソナ適合度
- 総合スコア

---

### 学習管理ダッシュボード
**URL**: http://localhost:8502

学習進捗管理：
- 学習時間トラッキング
- セッション履歴
- 目標管理
- 統計グラフ

---

## 🔧 サービス概要

| サービス | URL | 説明 |
|---------|-----|------|
| Open WebUI | http://localhost:3000 | LLMチャット |
| Grafana | http://localhost:3001 | モニタリング |
| Adminer | http://localhost:8080 | PostgreSQL管理 |
| Mongo Express | http://localhost:8081 | MongoDB管理 |
| Qdrant | http://localhost:6333/dashboard | ベクトルDB管理 |
| Prometheus | http://localhost:9090 | メトリクス収集 |
| LLM Dashboard | http://localhost:8501 | LLM評価 |
| Learning Dashboard | http://localhost:8502 | 学習管理 |

---

## 📸 スクリーンショット撮影方法

実際のスクリーンショットを撮影する手順：

```bash
# 1. 全サービス起動
make up

# 2. ヘルスチェック
make health

# 3. 各URLにアクセスしてスクリーンショット撮影
# - ブラウザで各URLを開く
# - Command + Shift + 4 (macOS) でスクリーンショット
# - screenshots/ フォルダに保存
```

---

## 🎨 推奨スクリーンショット

以下のスクリーンショットを撮影することを推奨します：

1. **Grafanaダッシュボード全体** - メトリクス表示
2. **Open WebUI** - チャット画面
3. **Qdrant Dashboard** - ベクトル検索結果
4. **Adminer** - PostgreSQLテーブル一覧
5. **LLM Dashboard** - モデル比較グラフ
6. **Learning Dashboard** - 学習統計

---

**注意**: スクリーンショットファイルは `screenshots/` フォルダに保存してください。
