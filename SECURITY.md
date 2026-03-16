# Security Policy / セキュリティポリシー

## 🔒 Reporting Security Vulnerabilities / セキュリティ脆弱性の報告

LocalDBKitのセキュリティ脆弱性を発見した場合は、**公開Issueではなく**、
以下の方法で報告してください。

If you discover a security vulnerability in LocalDBKit, please report it
**privately** using one of the methods below, NOT as a public issue.

---

## 📮 報告方法 / How to Report

### 方法1: GitHub Security Advisories（推奨）

1. [Security Advisories](https://github.com/HalkPapa/LocalDBKit/security/advisories/new) にアクセス
2. 「Report a vulnerability」をクリック
3. 詳細を記入して送信

### 方法2: Email

Email: security@localdbkit.dev

件名: `[SECURITY] LocalDBKit Vulnerability Report`

**注意**: メールアドレスは準備中です。現在はGitHub Security Advisoriesをご利用ください。
**Note**: Email address is under preparation. Please use GitHub Security Advisories for now.

---

## 📋 報告に含めるべき情報 / Information to Include

脆弱性の報告には、以下の情報を含めてください:

### 1. 脆弱性の種類 / Vulnerability Type
- [ ] SQL Injection
- [ ] XSS (Cross-Site Scripting)
- [ ] CSRF (Cross-Site Request Forgery)
- [ ] 認証バイパス / Authentication Bypass
- [ ] 権限昇格 / Privilege Escalation
- [ ] 情報漏洩 / Information Disclosure
- [ ] コードインジェクション / Code Injection
- [ ] その他 / Other: _______

### 2. 影響範囲 / Impact
```
影響を受けるバージョン:
影響を受けるコンポーネント:
CVSSスコア（分かれば）:
```

### 3. 脆弱性の詳細 / Vulnerability Details
```
詳細な説明:
再現手順:
概念実証（PoC）コード（任意）:
```

### 4. 提案する修正方法 / Suggested Fix (Optional)
```
修正案があれば記載してください
```

---

## ⏱️ 対応プロセス / Response Process

### タイムライン

| ステップ | 目標期間 |
|---------|---------|
| **受領確認** | 24時間以内 |
| **初期評価** | 3営業日以内 |
| **修正開発** | 重大度に応じて |
| **パッチリリース** | 重大度に応じて |
| **公開通知** | 修正後30日以内 |

### 重大度による対応時間

| 重大度 | 説明 | 目標修正時間 |
|--------|------|-------------|
| **Critical** | リモートコード実行、認証バイパス | 1週間以内 |
| **High** | データ漏洩、権限昇格 | 2週間以内 |
| **Medium** | XSS、CSRF | 1ヶ月以内 |
| **Low** | 情報漏洩（軽微） | 次回リリース |

---

## ✅ 対応フロー / Response Flow

```
1. 【報告受領】
   ↓
2. 【確認メール送信】（24時間以内）
   ↓
3. 【脆弱性の検証】（3営業日以内）
   ↓
4. 【重大度の評価】（CVSS v3.1基準）
   ↓
5. 【修正開発】
   ↓
6. 【報告者によるレビュー】（任意）
   ↓
7. 【パッチリリース】
   ↓
8. 【セキュリティアドバイザリ公開】（30日後）
   ↓
9. 【報告者のクレジット表示】（希望者のみ）
```

---

## 🎖️ 謝辞ポリシー / Acknowledgment Policy

セキュリティ脆弱性を責任を持って報告してくださった方には、
以下の形で謝辞を表明します（希望者のみ）:

For responsible disclosure of security vulnerabilities, we acknowledge
contributors in the following ways (optional):

1. **SECURITY.md の Hall of Fame に記載**
   - お名前（またはハンドル名）
   - 報告日
   - 脆弱性の種類（概要）

2. **リリースノートでのクレジット**
   - パッチリリース時のCHANGELOG.md

3. **謝礼（将来的に検討）**
   - 現在は提供していませんが、将来的に検討中

---

## 🚫 対象外 / Out of Scope

以下は脆弱性として扱いません:

- ✕ ソーシャルエンジニアリング
- ✕ DoS/DDoS攻撃
- ✕ 既知の脆弱性を含む依存ライブラリ（Dependabot で管理）
- ✕ 開発環境のみで発生する問題
- ✕ デフォルト設定の弱さ（ドキュメントで警告済み）
- ✕ 自己招いたセキュリティ問題（`.env`の誤設定など）

---

## 🛡️ Supported Versions / サポート対象バージョン

| Version | Supported |
|---------|-----------|
| 0.3.x (current) | ✅ Yes |
| 0.2.x | ⚠️ Critical fixes only |
| < 0.2.0 | ❌ No |

---

## 📜 脆弱性開示ポリシー / Vulnerability Disclosure Policy

### 責任ある開示 / Responsible Disclosure

LocalDBKitは**責任ある開示（Responsible Disclosure）**を推奨します:

1. **非公開で報告** - 公開Issueではなくプライベートに報告
2. **修正時間の提供** - 修正のための合理的な時間を提供
3. **協調的対応** - 修正プロセスで協力
4. **遅延開示** - 修正後30日間は詳細を公開しない

### 研究者の権利 / Researcher Rights

セキュリティ研究者には以下の権利があります:

- ✅ 非公開環境での脆弱性調査
- ✅ 報告内容のクレジット表示（希望者のみ）
- ✅ 修正後の詳細公開（30日経過後）

---

## 📞 連絡先 / Contact

- **GitHub Security Advisories**: https://github.com/HalkPapa/LocalDBKit/security/advisories/new (推奨 / Recommended)
- **Email**: security@localdbkit.dev (準備中 / Under preparation)
- **PGP Key**: https://github.com/HalkPapa/LocalDBKit/security/pgp-key.asc (準備中 / Under preparation)

---

## 🏆 Hall of Fame / 殿堂入り

責任を持ってセキュリティ脆弱性を報告してくださった方々:

<!-- 現在なし / None yet -->

---

## 📖 関連ドキュメント / Related Documents

- [LICENSE](LICENSE) - ソフトウェアライセンス
- [CONTRIBUTING.md](CONTRIBUTING.md) - 貢献ガイドライン
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - 行動規範（準備中）

---

**最終更新 / Last Updated**: 2026-03-16
**バージョン / Version**: 1.0
