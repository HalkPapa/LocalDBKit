# Changelog

All notable changes to LocalDBKit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- None

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

---

## [1.0.0] - 2026-03-16

### Added
- **Initial Public Release** / 初回公開リリース
- Complete Docker Compose environment with:
  - PostgreSQL 16 with pgvector extension
  - MongoDB 7
  - Redis 7
  - Qdrant vector database
- Management UIs:
  - Adminer (PostgreSQL)
  - Mongo Express (MongoDB)
  - Redis Commander (Redis)
  - Qdrant Dashboard
- Ollama LLM integration (optional)
- RAG system with FastAPI
- Comprehensive documentation:
  - README.md (Japanese)
  - README_EN.md (English)
  - CONTRIBUTING.md
  - SECURITY.md
  - CODE_OF_CONDUCT.md
  - THIRD_PARTY_LICENSES.md
- GitHub Issue Templates:
  - Bug Report
  - Feature Request
  - Security Advisory link
- Makefile with convenient commands
- Health check script
- Example code and tutorials
- License: Timed Personal Use License v1.1
  - Free for personal use and small businesses
  - Automatic conversion to Apache 2.0 on 2029-03-16
- Dependabot configuration for automated dependency updates

### Security
- Security vulnerability reporting process
- Responsible disclosure policy
- Comprehensive liability disclaimers

---

## [0.3.0] - 2026-03-11 (Internal)

### Added
- Multi-model LLM support (Gemini, Gemma2, Qwen2.5)
- Model evaluation guide
- RAG system enhancements

### Changed
- Improved documentation structure
- Enhanced Docker Compose configuration

---

## [0.2.0] - 2026-03-08 (Internal)

### Added
- Qdrant vector database integration
- Ollama LLM support
- Basic RAG functionality

### Changed
- Refactored database initialization scripts
- Updated Docker images to latest stable versions

---

## [0.1.0] - 2026-03-01 (Internal)

### Added
- Initial project structure
- PostgreSQL, MongoDB, Redis setup
- Basic Docker Compose configuration
- Management UIs (Adminer, Mongo Express)

---

## Version Comparison / バージョン比較

| Version | Status | Release Date | Key Features |
|---------|--------|--------------|--------------|
| 1.0.0 | ✅ **Public** | 2026-03-16 | 公開リリース、完全なドキュメント |
| 0.3.0 | Internal | 2026-03-11 | マルチモデルLLM、RAG強化 |
| 0.2.0 | Internal | 2026-03-08 | Qdrant、Ollama統合 |
| 0.1.0 | Internal | 2026-03-01 | 初期プロジェクト構造 |

---

## Migration Guides / 移行ガイド

### Upgrading to 1.0.0 from 0.3.0

**Breaking Changes**: None / なし

**New Files**:
- `CODE_OF_CONDUCT.md`
- `THIRD_PARTY_LICENSES.md`
- `CHANGELOG.md`
- `.github/dependabot.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`

**Steps**:
1. Pull latest changes: `git pull origin main`
2. Review new documentation files
3. Update `.env` if needed
4. Restart services: `make restart`

---

## Links / リンク

- [GitHub Repository](https://github.com/HalkPapa/LocalDBKit)
- [Issue Tracker](https://github.com/HalkPapa/LocalDBKit/issues)
- [Discussions](https://github.com/HalkPapa/LocalDBKit/discussions)
- [Security Advisories](https://github.com/HalkPapa/LocalDBKit/security/advisories)

---

**Legend / 凡例**:
- `Added` / 追加: 新機能
- `Changed` / 変更: 既存機能の変更
- `Deprecated` / 非推奨: 将来削除予定の機能
- `Removed` / 削除: 削除された機能
- `Fixed` / 修正: バグ修正
- `Security` / セキュリティ: セキュリティ関連の変更
