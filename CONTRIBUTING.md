# Contributing to LocalDBKit

LocalDBKitへの貢献に興味を持っていただき、ありがとうございます！🎉

## 🤝 貢献方法

### バグ報告

バグを見つけた場合：

1. [Issues](https://github.com/HalkPapa/LocalDBKit/issues)で既存の報告を確認
2. 新しいissueを作成
3. 以下の情報を含める：
   - バグの説明
   - 再現手順
   - 期待される動作
   - 実際の動作
   - 環境情報（OS、Dockerバージョンなど）

### 機能リクエスト

新機能の提案：

1. [Issues](https://github.com/HalkPapa/LocalDBKit/issues)で提案を検索
2. Feature Requestを作成
3. ユースケースと実装案を説明

### プルリクエスト

コードの貢献：

1. **フォーク**してクローン
   ```bash
   git clone https://github.com/YOUR_USERNAME/LocalDBKit.git
   cd LocalDBKit
   ```

2. **ブランチ作成**
   ```bash
   git checkout -b feature/amazing-feature
   # または
   git checkout -b fix/bug-description
   ```

3. **開発環境セットアップ**
   ```bash
   cp .env.example .env
   make dev
   ```

4. **変更を実装**
   - コーディング規約に従う（下記参照）
   - 必要に応じてテスト追加
   - ドキュメント更新

5. **コミット**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

6. **プッシュ**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **プルリクエスト作成**
   - 変更内容を明確に説明
   - 関連issueをリンク
   - スクリーンショット（UI変更の場合）

## 📝 コーディング規約

### Python

- **フォーマット**: Black（`black .`）
- **Linter**: flake8（`flake8 .`）
- **行の長さ**: 127文字まで
- **命名規則**:
  - 変数・関数: `snake_case`
  - クラス: `PascalCase`
  - 定数: `UPPER_CASE`

### Shell Scripts

- **シェバン**: `#!/bin/bash`
- **エラーハンドリング**: `set -e`
- **実行権限**: `chmod +x`

### Docker

- **イメージ**: 公式イメージを優先
- **バージョン**: 明示的に指定
- **ヘルスチェック**: 必須

### ドキュメント

- **日本語**: メインドキュメント
- **英語**: README_EN.md（予定）
- **Markdown**: CommonMark準拠

## 🔍 コミットメッセージ

Conventional Commitsに従う：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `test`: テスト追加
- `chore`: その他

### 例

```
feat(rag): add multi-modal support

- 画像認識機能を追加
- 音声処理機能を追加
- テストケース追加

Closes #123
```

## ✅ プルリクエストチェックリスト

- [ ] コードがフォーマット済み（`black .`）
- [ ] Lintエラーなし（`flake8 .`）
- [ ] Docker Composeが正常動作（`make up && make health`）
- [ ] ドキュメント更新済み
- [ ] CHANGELOG.md更新（該当する場合）
- [ ] テスト追加（該当する場合）

## 🧪 テスト

```bash
# Docker環境テスト
make up
make health

# Python lint
flake8 .
black --check .

# Docker Compose構文チェック
docker compose config --quiet
```

## 📚 開発リソース

- [プロジェクト構造](README.md#-プロジェクト構造)
- [アーキテクチャ](docs/reference/ARCHITECTURE.md)
- [開発ロードマップ](ROADMAP.md)
- [Docker完全ガイド](docs/guides/DOCKER_GUIDE.md)

## 💬 コミュニケーション

- **Issues**: バグ報告・機能リクエスト
- **Discussions**: 質問・アイデア共有
- **Pull Requests**: コードレビュー

## 🤝 行動規範 / Code of Conduct

すべての貢献者は[行動規範](CODE_OF_CONDUCT.md)に従うことが期待されます。
敬意と思いやりをもってコミュニケーションしましょう。

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
Please communicate with respect and kindness.

## 📜 ライセンス

コントリビューションは[Timed Personal Use License](LICENSE)の下で公開されます。

プルリクエストを送信することで、あなたは以下に同意したものとみなされます:
- あなたの貢献がこのライセンスの下でLocalDBKitに統合されること
- LocalDBKitの作者に対して、あなたの貢献を使用・改変・配布する
  永続的・世界的・非独占的・ロイヤリティフリーのライセンスを付与すること

詳細は [LICENSE](LICENSE) の第10条をご確認ください。

---

**ありがとうございます！** 🙏

あなたの貢献がLocalDBKitをより良くします。
