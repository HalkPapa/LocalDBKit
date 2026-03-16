# Third-Party Licenses / サードパーティライセンス

LocalDBKitは以下のオープンソースソフトウェアを使用しています。

LocalDBKit uses the following open-source software components.

---

## 📦 Docker Images / Dockerイメージ

### 1. PostgreSQL with pgvector
- **Image**: `ankane/pgvector:latest`
- **Base**: PostgreSQL
- **License**: PostgreSQL License (similar to MIT/BSD)
- **Website**: https://github.com/ankane/pgvector
- **Purpose**: ベクトル検索機能付きPostgreSQL / Vector search enabled PostgreSQL

**PostgreSQL License**:
```
Permission to use, copy, modify, and distribute this software and its
documentation for any purpose, without fee, and without a written agreement
is hereby granted, provided that the above copyright notice and this
paragraph and the following two paragraphs appear in all copies.
```

---

### 2. Redis
- **Image**: `redis:7-alpine`
- **License**: BSD 3-Clause License (Redis Source Available License 2.0 for Redis 7.4+)
- **Website**: https://redis.io/
- **Purpose**: キャッシュ・キューイング / Cache and queueing

**BSD 3-Clause License** (Redis < 7.4):
```
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
- Redistributions of source code must retain copyright notice
- Redistributions in binary form must reproduce copyright notice
- Neither the name of Redis nor contributors may be used to endorse products
```

**Note**: Redis 7.4以降はRSAL 2.0（Redis Source Available License）に変更されました。
詳細: https://redis.io/docs/about/license/

---

### 3. MongoDB
- **Image**: `mongo:7`
- **License**: Server Side Public License (SSPL) v1
- **Website**: https://www.mongodb.com/
- **Purpose**: ドキュメント型データベース / Document database

**SSPL v1**:
- オープンソースライセンスではありますが、サービス提供者に追加の義務があります
- LocalDBKitはローカル開発環境での使用のみを想定しているため影響なし
- 詳細: https://www.mongodb.com/licensing/server-side-public-license

---

### 4. Qdrant
- **Image**: `qdrant/qdrant:latest`
- **License**: Apache License 2.0
- **Website**: https://qdrant.tech/
- **Purpose**: ベクトルデータベース / Vector database

**Apache License 2.0**:
```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

---

### 5. Adminer
- **Image**: `adminer:latest`
- **License**: Apache License 2.0 / GPL v2
- **Website**: https://www.adminer.org/
- **Purpose**: データベース管理UI / Database management UI

---

### 6. Mongo Express
- **Image**: `mongo-express:latest`
- **License**: MIT License
- **Website**: https://github.com/mongo-express/mongo-express
- **Purpose**: MongoDB管理UI / MongoDB management UI

**MIT License**:
```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

---

### 7. Redis Commander
- **Image**: `rediscommander/redis-commander:latest`
- **License**: MIT License
- **Website**: https://github.com/joeferner/redis-commander
- **Purpose**: Redis管理UI / Redis management UI
- **Note**: M1/M2 Mac互換性問題あり（代替: `redis-cli`）

---

### 8. Ollama (optional)
- **Image**: `ollama/ollama:latest`
- **License**: MIT License
- **Website**: https://ollama.ai/
- **Purpose**: ローカルLLM実行環境 / Local LLM runtime

---

## 🐍 Python Dependencies / Python依存関係

### FastAPI
- **License**: MIT License
- **Website**: https://fastapi.tiangolo.com/
- **Purpose**: API Gateway実装 / API Gateway implementation

### Psycopg2
- **License**: LGPL v3 (with linking exception)
- **Website**: https://www.psycopg.org/
- **Purpose**: PostgreSQL接続 / PostgreSQL connector

### PyMongo
- **License**: Apache License 2.0
- **Website**: https://pymongo.readthedocs.io/
- **Purpose**: MongoDB接続 / MongoDB connector

### Redis-py
- **License**: MIT License
- **Website**: https://github.com/redis/redis-py
- **Purpose**: Redis接続 / Redis connector

### Qdrant-client
- **License**: Apache License 2.0
- **Website**: https://github.com/qdrant/qdrant-client
- **Purpose**: Qdrant接続 / Qdrant connector

---

## 📜 License Compatibility / ライセンス互換性

LocalDBKitの「Timed Personal Use License」は、以下の依存関係と互換性があります：

LocalDBKit's "Timed Personal Use License" is compatible with the following dependencies:

| Component | License | 商用利用 | 再配布 | 互換性 |
|-----------|---------|----------|--------|--------|
| PostgreSQL | PostgreSQL License | ✅ | ✅ | ✅ |
| Redis | BSD 3-Clause / RSAL | ✅ | ⚠️ | ✅ |
| MongoDB | SSPL v1 | ✅ | ⚠️ | ✅ |
| Qdrant | Apache 2.0 | ✅ | ✅ | ✅ |
| Adminer | Apache 2.0 / GPL v2 | ✅ | ✅ | ✅ |
| Mongo Express | MIT | ✅ | ✅ | ✅ |
| Ollama | MIT | ✅ | ✅ | ✅ |

**凡例 / Legend**:
- ✅ = 問題なし / No issues
- ⚠️ = 条件付き / Conditional (see license terms)

---

## 🔍 License Notices / ライセンス表記

### SSPL (MongoDB) について

MongoDB ServerはSSPL v1ライセンスです。これは、MongoDBをサービスとして提供する場合、サービス全体のソースコードを公開する義務が生じる可能性があります。

**LocalDBKitへの影響**:
- ✅ ローカル開発環境での使用: 影響なし
- ✅ 個人プロジェクトでの使用: 影響なし
- ⚠️ MongoDBをサービスとして提供: SSPL義務が発生する可能性

詳細: https://www.mongodb.com/licensing/server-side-public-license/faq

### RSAL (Redis) について

Redis 7.4以降はRSAL 2.0（Redis Source Available License）が適用されます。

**LocalDBKitへの影響**:
- ✅ ローカル開発環境での使用: 影響なし
- ✅ 個人プロジェクトでの使用: 影響なし
- ⚠️ Redisをサービスとして提供: 制限あり

詳細: https://redis.io/docs/about/license/

---

## 📚 Full License Texts / 完全なライセンステキスト

完全なライセンステキストは以下から入手できます：

Full license texts are available at:

- **MIT License**: https://opensource.org/licenses/MIT
- **Apache License 2.0**: https://www.apache.org/licenses/LICENSE-2.0
- **BSD 3-Clause**: https://opensource.org/licenses/BSD-3-Clause
- **PostgreSQL License**: https://opensource.org/licenses/postgresql
- **SSPL v1**: https://www.mongodb.com/licensing/server-side-public-license
- **RSAL 2.0**: https://redis.io/docs/about/license/
- **GPL v2**: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
- **LGPL v3**: https://www.gnu.org/licenses/lgpl-3.0.html

---

## 🔄 Updates / 更新履歴

依存関係のライセンス変更を追跡します：

| 日付 | 変更内容 | 影響 |
|------|----------|------|
| 2024-03-20 | Redis 7.4がRSAL 2.0に変更 | ローカル使用には影響なし |
| 2018-10-16 | MongoDB ServerがSSPLに変更 | ローカル使用には影響なし |

---

## ⚠️ Disclaimer / 免責事項

このドキュメントは情報提供を目的としており、法的助言ではありません。ライセンスの解釈や適用については、必要に応じて法律専門家にご相談ください。

This document is for informational purposes only and does not constitute legal advice. Please consult with a legal professional regarding license interpretation or application.

---

## 📞 Contact / お問い合わせ

ライセンスに関する質問や懸念事項がある場合：

If you have questions or concerns about licensing:

- **GitHub Issues**: https://github.com/HalkPapa/LocalDBKit/issues
- **Email**: licensing@localdbkit.dev (準備中)

---

**最終更新 / Last Updated**: 2026-03-16
**バージョン / Version**: 1.0
