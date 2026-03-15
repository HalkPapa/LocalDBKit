# ドキュメント索引

このフォルダにはデータベース構築プロジェクトの全ドキュメントが含まれています。

**最終更新**: 2026年3月15日

---

## 📚 目次

### 🚀 クイックスタート

初めての方はこちらから：
- **[QUICKSTART.md](guides/QUICKSTART.md)** - 5分で始めるクイックスタート

### 📖 ガイド

ステップバイステップのガイドドキュメント：

| ガイド | 内容 | 対象 |
|--------|------|------|
| [SETUP_GUIDE.md](guides/SETUP_GUIDE.md) | 初期セットアップ完全ガイド | 初心者 |
| [DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) | Docker操作完全ガイド | 初心者〜中級者 |
| [FLOW_GUIDE.md](guides/FLOW_GUIDE.md) | システム使用フロー完全ガイド | 全員 |
| [LLM_GUIDE.md](guides/LLM_GUIDE.md) | LLM使用ガイド | LLM利用者 |
| [MULTI_APP_GUIDE.md](guides/MULTI_APP_GUIDE.md) | 複数アプリ管理ガイド | アプリ開発者 |

### 📋 リファレンス

技術仕様とアーキテクチャ：

| ドキュメント | 内容 |
|-------------|------|
| [ARCHITECTURE.md](reference/ARCHITECTURE.md) | システムアーキテクチャ詳細 |
| [DATABASES.md](reference/DATABASES.md) | データベース仕様 |
| [APP_DATABASE_MAP.md](reference/APP_DATABASE_MAP.md) | アプリとDBのマッピング |

### 🎨 図・ダイアグラム

視覚的なシステム構成図：

| ファイル | 種類 | 用途 |
|---------|------|------|
| [architecture.drawio](diagrams/architecture.drawio) | draw.io | アーキテクチャ図（編集可能） |
| [architecture.svg](diagrams/architecture.svg) | SVG画像 | アーキテクチャ図（表示用） |
| [flow.drawio](diagrams/flow.drawio) | draw.io | フロー図（編集可能） |

### 📝 プロジェクト情報

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - プロジェクト全体サマリー（エージェント向け）
- **[WORK_LOG.md](WORK_LOG.md)** - 構築作業ログ・トラブルシューティング履歴

---

## 🎯 目的別ガイド

### 初めて使う
1. [QUICKSTART.md](guides/QUICKSTART.md) で起動
2. [FLOW_GUIDE.md](guides/FLOW_GUIDE.md) で使い方を理解

### セットアップしたい
1. [SETUP_GUIDE.md](guides/SETUP_GUIDE.md) で環境構築
2. [DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) でDocker操作を学ぶ

### LLMを使いたい
1. [LLM_GUIDE.md](guides/LLM_GUIDE.md) でLLM使用法を確認
2. [FLOW_GUIDE.md](guides/FLOW_GUIDE.md) のフロー1参照

### アプリ開発したい
1. [MULTI_APP_GUIDE.md](guides/MULTI_APP_GUIDE.md) でマルチアプリ管理を学ぶ
2. [APP_DATABASE_MAP.md](reference/APP_DATABASE_MAP.md) でDB選定

### アーキテクチャを理解したい
1. [ARCHITECTURE.md](reference/ARCHITECTURE.md) でシステム構成を確認
2. [diagrams/](diagrams/) で図を参照

### トラブルシューティング
1. [DOCKER_GUIDE.md](guides/DOCKER_GUIDE.md) のトラブルシューティングセクション
2. [WORK_LOG.md](WORK_LOG.md) で過去の問題と解決策を確認

---

## 📂 フォルダ構造

```
docs/
├── README.md                    ← このファイル（索引）
│
├── guides/                      ← ガイドドキュメント
│   ├── QUICKSTART.md           - クイックスタート
│   ├── SETUP_GUIDE.md          - セットアップガイド
│   ├── DOCKER_GUIDE.md         - Docker操作ガイド
│   ├── FLOW_GUIDE.md           - 使用フローガイド
│   ├── LLM_GUIDE.md            - LLM使用ガイド
│   └── MULTI_APP_GUIDE.md      - マルチアプリ管理ガイド
│
├── reference/                   ← リファレンス
│   ├── ARCHITECTURE.md         - アーキテクチャ詳細
│   ├── DATABASES.md            - データベース仕様
│   └── APP_DATABASE_MAP.md     - アプリ・DB マッピング
│
├── diagrams/                    ← 図・ダイアグラム
│   ├── architecture.drawio     - アーキテクチャ図（編集可）
│   ├── architecture.svg        - アーキテクチャ図（画像）
│   └── flow.drawio             - フロー図（編集可）
│
├── PROJECT_SUMMARY.md           ← プロジェクトサマリー
└── WORK_LOG.md                  ← 作業ログ
```

---

## 🔄 ドキュメント更新履歴

| 日付 | 更新内容 |
|------|---------|
| 2026-03-15 | docs/フォルダ整理、README作成 |
| 2026-03-15 | FLOW_GUIDE.md追加 |
| 2026-03-15 | ARCHITECTURE.md、flow.drawio追加 |
| 2026-03-09 | DOCKER_GUIDE.md、PROJECT_SUMMARY.md作成 |
| 2026-03-09 | 初期ドキュメント作成 |

---

## 🤝 貢献

ドキュメントの改善提案や誤字脱字の報告は歓迎します。

---

**プロジェクト**: データベース構築 - 完全ローカル開発環境
**作成者**: Claude Sonnet 4.5 (Anthropic)
**ライセンス**: プロジェクト内部使用
