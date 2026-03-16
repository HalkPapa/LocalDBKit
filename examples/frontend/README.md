# Frontend Examples / フロントエンド実装例

LocalDBKit APIをフロントエンド（JavaScript/TypeScript）から使用する実装例です。

---

## 📁 ファイル一覧

| ファイル | 言語 | 説明 |
|---------|------|------|
| `fetch-example.js` | JavaScript | Fetch APIを使用した実装例 |
| `typescript-example.ts` | TypeScript | 型安全なクライアント実装 |

---

## 🚀 クイックスタート

### 前提条件

1. **LocalDBKitが起動していること**
```bash
cd /path/to/LocalDBKit
make up
make health
```

2. **CORS設定が適切であること**
   - デフォルトで`allow_origins=["*"]`（開発環境向け）
   - 本番環境では適切なオリジンに制限してください

---

## 📘 JavaScript（Fetch API）の使い方

### ブラウザで使用

1. **HTMLファイルを作成**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>LocalDBKit Example</title>
</head>
<body>
  <h1>LocalDBKit API Example</h1>
  <button onclick="main()">Run Example</button>

  <script src="fetch-example.js"></script>
</body>
</html>
```

2. **ブラウザで開く**
   - HTTPサーバーで配信（CORS制約回避）
   ```bash
   # Python 3
   python3 -m http.server 8000

   # Node.js
   npx http-server
   ```

3. **ボタンをクリックして実行**

### Node.jsで使用

```bash
# node-fetch をインストール（Node.js 17以下の場合）
npm install node-fetch

# 実行
node fetch-example.js
```

---

## 📗 TypeScript の使い方

### 1. 依存関係のインストール

```bash
npm init -y
npm install axios
npm install --save-dev typescript @types/node ts-node
```

### 2. 実行

```bash
npx ts-node typescript-example.ts
```

### 3. プロジェクトで使用

#### インポート
```typescript
import { LocalDBKitClient } from './typescript-example';

const client = new LocalDBKitClient('http://localhost:8000/api/v1');
```

#### 型定義を活用
```typescript
import type { RAGQueryResponse, LLMModel } from './typescript-example';

const models: LLMModel[] = await client.getModels();
const ragResponse: RAGQueryResponse = await client.ragQuery({ query: 'test' });
```

---

## 🎯 主な機能

### 1. 認証（JWT）

**JavaScript**:
```javascript
await login('admin', 'admin');
```

**TypeScript**:
```typescript
const token = await client.login('admin', 'admin');
```

---

### 2. LLMチャット

**JavaScript**:
```javascript
const response = await chat('What is LocalDBKit?', 'gemma2:9b');
console.log(response);
```

**TypeScript**:
```typescript
const response = await client.chat({
  prompt: 'What is LocalDBKit?',
  model: 'gemma2:9b',
  options: {
    temperature: 0.7,
    max_tokens: 500
  }
});
console.log(response);
```

---

### 3. RAGドキュメント追加

**JavaScript**:
```javascript
await addDocument(
  'This is my knowledge',
  'my_collection',
  { category: 'tutorial' }
);
```

**TypeScript**:
```typescript
await client.addDocument({
  content: 'This is my knowledge',
  collection: 'my_collection',
  metadata: { category: 'tutorial' }
});
```

---

### 4. RAGクエリ

**JavaScript**:
```javascript
const result = await ragQuery('What did I say about tutorials?', 'my_collection');
console.log(result.answer);
console.log(result.sources);
```

**TypeScript**:
```typescript
const result = await client.ragQuery({
  query: 'What did I say about tutorials?',
  collection: 'my_collection',
  use_llm: true,
  top_k: 5
});
console.log(result.answer);
result.sources.forEach(source => {
  console.log(`- [Score: ${source.score}] ${source.text}`);
});
```

---

### 5. 画像アップロード（OCR）

**JavaScript（ブラウザ）**:
```javascript
// ファイル入力から取得
const fileInput = document.getElementById('file-input');
const file = fileInput.files[0];

const result = await addImageDocument(file, 'my_images');
console.log(`Extracted text: ${result.extracted_text}`);
console.log(`OCR confidence: ${result.ocr_confidence}%`);
```

**TypeScript**:
```typescript
// Node.js環境
import * as fs from 'fs';

const fileBuffer = fs.readFileSync('test-image.png');
const result = await client.addImageDocument(fileBuffer, 'test-image.png', 'my_images');
console.log(result.extracted_text);
```

---

### 6. PDFアップロード

**JavaScript（ブラウザ）**:
```javascript
const fileInput = document.getElementById('pdf-input');
const file = fileInput.files[0];

const result = await addPDFDocument(file, 'my_documents');
console.log(`Pages: ${result.page_count}`);
console.log(`Words: ${result.word_count}`);
```

**TypeScript**:
```typescript
const fileBuffer = fs.readFileSync('document.pdf');
const result = await client.addPDFDocument(fileBuffer, 'document.pdf', 'my_documents');
```

---

## 🔐 エラーハンドリング

### 統一されたエラーレスポンス形式

```typescript
interface ErrorResponse {
  detail: string;        // エラーメッセージ
  error_code?: string;   // エラーコード（将来拡張用）
  timestamp?: string;    // タイムスタンプ（将来拡張用）
}
```

### HTTPステータスコードと意味

| コード | 意味 | 対処法 |
|--------|------|--------|
| 200 | 成功 | - |
| 401 | 認証エラー | `login()`を実行してトークンを取得 |
| 403 | 権限エラー | ユーザー権限を確認 |
| 404 | リソース不在 | URLやIDを確認 |
| 429 | レート制限超過 | しばらく待ってから再試行 |
| 500 | サーバーエラー | サーバーログを確認 |

### エラーハンドリング例

**JavaScript**:
```javascript
try {
  const response = await chat('test');
} catch (error) {
  if (error.message.includes('401')) {
    console.error('Please login first');
    await login('admin', 'admin');
  } else if (error.message.includes('429')) {
    console.error('Rate limit exceeded, waiting...');
    await new Promise(resolve => setTimeout(resolve, 60000)); // 1分待機
  } else {
    console.error('Unexpected error:', error);
  }
}
```

**TypeScript**:
```typescript
import { AxiosError } from 'axios';

try {
  const response = await client.chat({ prompt: 'test' });
} catch (error) {
  if (error instanceof AxiosError) {
    if (error.response?.status === 401) {
      console.error('Authentication required');
      await client.login('admin', 'admin');
    } else if (error.response?.status === 429) {
      const resetHeader = error.response.headers['x-ratelimit-reset'];
      const resetTime = new Date(parseInt(resetHeader) * 1000);
      console.error(`Rate limit exceeded. Resets at ${resetTime}`);
    }
  }
}
```

---

## ⏱️ レート制限

### デフォルト設定

- **制限**: 100リクエスト/分
- **ウィンドウ**: 1分間

### レート制限ヘッダー

すべてのレスポンスに以下のヘッダーが含まれます:

```
X-RateLimit-Limit: 100          # 1分あたりの上限
X-RateLimit-Remaining: 99       # 残りリクエスト数
X-RateLimit-Reset: 1234567890   # リセット時刻（Unix timestamp）
```

### レート制限チェック例

**JavaScript**:
```javascript
function checkRateLimitHeaders(response) {
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');

  if (remaining / limit < 0.1) {
    console.warn('⚠️ Rate limit almost exceeded!');
  }
}
```

**TypeScript**:
```typescript
// クライアント内で自動チェック（実装済み）
// 残り10%を切ると自動的に警告が表示されます
```

---

## 🔧 CORS設定

### 開発環境（デフォルト）

```python
# apps/api-gateway/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 本番環境（推奨）

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**カスタマイズ方法**:
1. `apps/api-gateway/main.py`を編集
2. `allow_origins`に許可するオリジンを指定
3. コンテナを再起動: `make restart`

---

## 📝 完全なHTMLサンプル

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LocalDBKit Chat</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
    #chat { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
    #input { width: 80%; padding: 10px; }
    #send { padding: 10px 20px; }
    .message { margin: 10px 0; }
    .user { color: blue; }
    .assistant { color: green; }
  </style>
</head>
<body>
  <h1>LocalDBKit Chat</h1>
  <div id="status">ログイン中...</div>
  <div id="chat"></div>
  <input type="text" id="input" placeholder="メッセージを入力..." />
  <button id="send">送信</button>

  <script src="fetch-example.js"></script>
  <script>
    const chatDiv = document.getElementById('chat');
    const inputField = document.getElementById('input');
    const sendButton = document.getElementById('send');
    const statusDiv = document.getElementById('status');

    // 初期化
    (async () => {
      try {
        await login('admin', 'admin');
        statusDiv.textContent = '✅ 準備完了';
        statusDiv.style.color = 'green';
      } catch (error) {
        statusDiv.textContent = '❌ ログイン失敗';
        statusDiv.style.color = 'red';
      }
    })();

    // メッセージ送信
    sendButton.addEventListener('click', async () => {
      const message = inputField.value.trim();
      if (!message) return;

      // ユーザーメッセージ表示
      chatDiv.innerHTML += `<div class="message user"><strong>You:</strong> ${message}</div>`;
      inputField.value = '';

      try {
        // LLMに送信
        const response = await chat(message);

        // アシスタント応答表示
        chatDiv.innerHTML += `<div class="message assistant"><strong>Assistant:</strong> ${response}</div>`;
        chatDiv.scrollTop = chatDiv.scrollHeight;
      } catch (error) {
        chatDiv.innerHTML += `<div class="message" style="color:red;"><strong>Error:</strong> ${error.message}</div>`;
      }
    });

    // Enterキーで送信
    inputField.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendButton.click();
    });
  </script>
</body>
</html>
```

---

## 🔗 関連ドキュメント

- [API Gateway完全ガイド](../../docs/guides/API_GATEWAY_GUIDE.md)
- [用語集（GLOSSARY.md）](../../docs/GLOSSARY.md)
- [アーキテクチャ](../../docs/reference/ARCHITECTURE.md)

---

## 🐛 トラブルシューティング

### CORS エラー

**エラー**:
```
Access to fetch at 'http://localhost:8000/api/v1/...' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**対処法**:
1. API GatewayのCORS設定を確認
2. `apps/api-gateway/main.py`の`allow_origins`を編集
3. `make restart`でコンテナ再起動

---

### 認証エラー (401)

**エラー**:
```
{"detail": "Not authenticated"}
```

**対処法**:
```javascript
// 再ログイン
await login('admin', 'admin');
```

---

### タイムアウトエラー

**エラー**:
```
timeout of 120000ms exceeded
```

**対処法**:
- LLM処理は時間がかかる場合があります
- タイムアウト値を増やす:
  ```typescript
  const client = new LocalDBKitClient('http://localhost:8000/api/v1');
  client.client.defaults.timeout = 300000; // 5分
  ```

---

## 📧 フィードバック

不明点や改善提案は [Issues](https://github.com/HalkPapa/LocalDBKit/issues) へ！

---

**最終更新**: 2026年3月16日
