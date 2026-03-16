/**
 * LocalDBKit API - JavaScript Fetch Example
 *
 * このファイルは、LocalDBKit APIをブラウザのFetch APIで使用する例です。
 *
 * 前提条件:
 * - LocalDBKitが http://localhost:8000 で起動していること
 * - CORS設定が適切に行われていること
 */

// =====================================
// 設定
// =====================================

const API_BASE_URL = 'http://localhost:8000/api/v1';
let authToken = null;

// =====================================
// 1. 認証 (JWT)
// =====================================

/**
 * ログインしてJWTトークンを取得
 */
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString()
    });

    if (!response.ok) {
      throw new Error(`Login failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    authToken = data.access_token;
    console.log('✅ Login successful');
    return authToken;
  } catch (error) {
    console.error('❌ Login error:', error);
    throw error;
  }
}

// =====================================
// 2. LLM API
// =====================================

/**
 * 利用可能なLLMモデル一覧を取得
 */
async function getModels() {
  try {
    const response = await fetch(`${API_BASE_URL}/llm/models`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`Get models failed: ${response.status}`);
    }

    const data = await response.json();
    console.log('📦 Available models:', data.models.length);
    return data.models;
  } catch (error) {
    console.error('❌ Get models error:', error);
    throw error;
  }
}

/**
 * LLMにチャットリクエストを送信
 */
async function chat(prompt, model = 'gemma2:9b') {
  try {
    const response = await fetch(`${API_BASE_URL}/llm/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        model: model,
        stream: false
      })
    });

    if (!response.ok) {
      // エラーレスポンスの詳細を取得
      const errorData = await response.json();
      throw new Error(`Chat failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log('💬 Chat response received');
    return data.response;
  } catch (error) {
    console.error('❌ Chat error:', error);
    throw error;
  }
}

// =====================================
// 3. RAG API
// =====================================

/**
 * RAGシステムにドキュメントを追加
 */
async function addDocument(content, collection = 'knowledge_base', metadata = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}/rag/documents`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: content,
        collection: collection,
        metadata: metadata
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Add document failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log(`📄 Document added: ${data.id}`);
    return data;
  } catch (error) {
    console.error('❌ Add document error:', error);
    throw error;
  }
}

/**
 * RAGクエリ（知識検索+LLM回答生成）
 */
async function ragQuery(query, collection = 'knowledge_base', useLLM = true) {
  try {
    const response = await fetch(`${API_BASE_URL}/rag/query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        collection: collection,
        use_llm: useLLM,
        top_k: 5
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`RAG query failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log('🔍 RAG query completed');
    console.log(`   Sources found: ${data.sources.length}`);
    return data;
  } catch (error) {
    console.error('❌ RAG query error:', error);
    throw error;
  }
}

/**
 * 画像ファイルをRAGシステムに追加（OCR処理）
 */
async function addImageDocument(file, collection = 'knowledge_base') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('collection', collection);

  try {
    const response = await fetch(`${API_BASE_URL}/rag/documents/image`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        // Content-Type は自動設定されるので指定不要
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Add image failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log(`🖼️  Image processed: ${data.filename}`);
    console.log(`   OCR confidence: ${data.ocr_confidence}%`);
    return data;
  } catch (error) {
    console.error('❌ Add image error:', error);
    throw error;
  }
}

/**
 * PDFファイルをRAGシステムに追加
 */
async function addPDFDocument(file, collection = 'knowledge_base') {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('collection', collection);

  try {
    const response = await fetch(`${API_BASE_URL}/rag/documents/pdf`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Add PDF failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();
    console.log(`📑 PDF processed: ${data.filename}`);
    console.log(`   Pages: ${data.page_count}, Words: ${data.word_count}`);
    return data;
  } catch (error) {
    console.error('❌ Add PDF error:', error);
    throw error;
  }
}

// =====================================
// 4. レート制限のチェック
// =====================================

/**
 * レート制限情報を確認
 */
function checkRateLimitHeaders(response) {
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');

  if (limit) {
    console.log(`⏱️  Rate Limit: ${remaining}/${limit} remaining`);
    if (reset) {
      const resetDate = new Date(parseInt(reset) * 1000);
      console.log(`   Resets at: ${resetDate.toLocaleString()}`);
    }
  }
}

// =====================================
// 5. エラーハンドリング例
// =====================================

/**
 * 統一されたエラーハンドラ
 */
async function handleAPICall(apiFunction, ...args) {
  try {
    return await apiFunction(...args);
  } catch (error) {
    if (error.message.includes('401')) {
      console.error('🔐 Authentication required. Please login first.');
    } else if (error.message.includes('429')) {
      console.error('⏱️  Rate limit exceeded. Please wait and try again.');
    } else if (error.message.includes('500')) {
      console.error('🔥 Server error. Please check server logs.');
    } else {
      console.error('❌ Unexpected error:', error);
    }
    throw error;
  }
}

// =====================================
// 使用例
// =====================================

async function main() {
  try {
    // 1. ログイン
    await login('admin', 'admin');

    // 2. モデル一覧取得
    const models = await getModels();
    console.log('Available models:', models.map(m => m.name));

    // 3. チャット
    const response = await chat('Hello! What is LocalDBKit?');
    console.log('Chat response:', response);

    // 4. RAGドキュメント追加
    await addDocument('LocalDBKit is a complete local database development kit.', 'knowledge_base', {
      category: 'documentation'
    });

    // 5. RAGクエリ
    const ragResponse = await ragQuery('What is LocalDBKit?');
    console.log('RAG answer:', ragResponse.answer);
    console.log('Sources:', ragResponse.sources.length);

  } catch (error) {
    console.error('Main error:', error);
  }
}

// HTMLから使用する場合の例
// <button onclick="main()">Run Example</button>

// Node.js環境で実行する場合
// node fetch-example.js

// ブラウザコンソールで実行する場合
// このファイルをHTMLに<script>タグで読み込んで、main()を実行

console.log('📘 LocalDBKit Fetch API Example loaded');
console.log('   Run main() to execute the example');
