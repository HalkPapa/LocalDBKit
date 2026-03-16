/**
 * LocalDBKit API - TypeScript Example
 *
 * このファイルは、LocalDBKit APIをTypeScriptで型安全に使用する例です。
 *
 * インストール:
 * npm install axios
 * npm install --save-dev @types/node
 *
 * 実行:
 * npx ts-node typescript-example.ts
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// =====================================
// 型定義
// =====================================

/** 認証レスポンス */
interface AuthResponse {
  access_token: string;
  token_type: string;
}

/** LLMモデル情報 */
interface LLMModel {
  name: string;
  size: number;
  modified_at: string;
  details?: {
    format?: string;
    family?: string;
    parameter_size?: string;
  };
}

/** モデル一覧レスポンス */
interface ModelsResponse {
  models: LLMModel[];
  count: number;
}

/** チャットリクエスト */
interface ChatRequest {
  prompt: string;
  model?: string;
  stream?: boolean;
  options?: {
    temperature?: number;
    max_tokens?: number;
  };
}

/** チャットレスポンス */
interface ChatResponse {
  response: string;
  model: string;
  created_at: string;
  done: boolean;
}

/** RAGドキュメント追加リクエスト */
interface AddDocumentRequest {
  content: string;
  collection?: string;
  metadata?: Record<string, any>;
}

/** RAGドキュメント追加レスポンス */
interface AddDocumentResponse {
  id: string;
  collection: string;
  status: string;
  preview: string;
}

/** RAGクエリリクエスト */
interface RAGQueryRequest {
  query: string;
  collection?: string;
  use_llm?: boolean;
  top_k?: number;
}

/** RAGソース */
interface RAGSource {
  id: string;
  text: string;
  score: number;
  metadata: Record<string, any>;
  source: string;
}

/** RAGクエリレスポンス */
interface RAGQueryResponse {
  query: string;
  answer: string;
  sources: RAGSource[];
}

/** エラーレスポンス */
interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

/** 画像アップロードレスポンス */
interface ImageUploadResponse {
  id: string;
  collection: string;
  source: string;
  filename: string;
  extracted_text: string;
  ocr_confidence: number;
}

/** PDFアップロードレスポンス */
interface PDFUploadResponse {
  id: string;
  collection: string;
  source: string;
  filename: string;
  page_count: number;
  word_count: number;
}

/** コレクション一覧レスポンス */
interface CollectionsResponse {
  collections: Array<{
    name: string;
    vectors_count?: number;
    points_count?: number;
  }>;
  count: number;
}

// =====================================
// LocalDBKit クライアント
// =====================================

class LocalDBKitClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 120000, // 2分（LLM処理考慮）
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // レスポンスインターセプター（レート制限チェック）
    this.client.interceptors.response.use(
      (response) => {
        this.checkRateLimitHeaders(response.headers);
        return response;
      },
      (error: AxiosError<ErrorResponse>) => {
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  // =====================================
  // 1. 認証
  // =====================================

  /**
   * ログイン
   */
  async login(username: string, password: string): Promise<string> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.client.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    this.authToken = response.data.access_token;

    // 以降のリクエストにトークンを自動付与
    this.client.defaults.headers.common['Authorization'] = `Bearer ${this.authToken}`;

    console.log('✅ Login successful');
    return this.authToken;
  }

  /**
   * ログアウト
   */
  logout(): void {
    this.authToken = null;
    delete this.client.defaults.headers.common['Authorization'];
    console.log('👋 Logged out');
  }

  // =====================================
  // 2. LLM API
  // =====================================

  /**
   * 利用可能なモデル一覧を取得
   */
  async getModels(): Promise<LLMModel[]> {
    const response = await this.client.get<ModelsResponse>('/llm/models');
    console.log(`📦 Available models: ${response.data.count}`);
    return response.data.models;
  }

  /**
   * LLMチャット
   */
  async chat(request: ChatRequest): Promise<string> {
    const response = await this.client.post<ChatResponse>('/llm/chat', {
      prompt: request.prompt,
      model: request.model || 'gemma2:9b',
      stream: request.stream || false,
      options: request.options || {},
    });

    console.log('💬 Chat response received');
    return response.data.response;
  }

  // =====================================
  // 3. RAG API
  // =====================================

  /**
   * ドキュメント追加
   */
  async addDocument(request: AddDocumentRequest): Promise<AddDocumentResponse> {
    const response = await this.client.post<AddDocumentResponse>('/rag/documents', {
      content: request.content,
      collection: request.collection || 'knowledge_base',
      metadata: request.metadata || {},
    });

    console.log(`📄 Document added: ${response.data.id}`);
    return response.data;
  }

  /**
   * RAGクエリ
   */
  async ragQuery(request: RAGQueryRequest): Promise<RAGQueryResponse> {
    const response = await this.client.post<RAGQueryResponse>('/rag/query', {
      query: request.query,
      collection: request.collection || 'knowledge_base',
      use_llm: request.use_llm !== undefined ? request.use_llm : true,
      top_k: request.top_k || 5,
    });

    console.log(`🔍 RAG query completed (${response.data.sources.length} sources)`);
    return response.data;
  }

  /**
   * 画像アップロード（OCR処理）
   */
  async addImageDocument(file: File | Buffer, filename: string, collection: string = 'knowledge_base'): Promise<ImageUploadResponse> {
    const formData = new FormData();

    // Fileオブジェクトまたは Buffer を適切に処理
    if (file instanceof Buffer) {
      formData.append('file', new Blob([file]), filename);
    } else {
      formData.append('file', file);
    }
    formData.append('collection', collection);

    const response = await this.client.post<ImageUploadResponse>('/rag/documents/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log(`🖼️  Image processed: ${response.data.filename}`);
    console.log(`   OCR confidence: ${response.data.ocr_confidence}%`);
    return response.data;
  }

  /**
   * PDFアップロード
   */
  async addPDFDocument(file: File | Buffer, filename: string, collection: string = 'knowledge_base'): Promise<PDFUploadResponse> {
    const formData = new FormData();

    if (file instanceof Buffer) {
      formData.append('file', new Blob([file], { type: 'application/pdf' }), filename);
    } else {
      formData.append('file', file);
    }
    formData.append('collection', collection);

    const response = await this.client.post<PDFUploadResponse>('/rag/documents/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log(`📑 PDF processed: ${response.data.filename}`);
    console.log(`   Pages: ${response.data.page_count}, Words: ${response.data.word_count}`);
    return response.data;
  }

  /**
   * コレクション一覧取得
   */
  async getCollections(): Promise<CollectionsResponse> {
    const response = await this.client.get<CollectionsResponse>('/rag/collections');
    console.log(`📚 Collections: ${response.data.count}`);
    return response.data;
  }

  // =====================================
  // ヘルパーメソッド
  // =====================================

  /**
   * レート制限ヘッダーのチェック
   */
  private checkRateLimitHeaders(headers: any): void {
    const limit = headers['x-ratelimit-limit'];
    const remaining = headers['x-ratelimit-remaining'];
    const reset = headers['x-ratelimit-reset'];

    if (limit !== undefined) {
      console.log(`⏱️  Rate Limit: ${remaining}/${limit} remaining`);

      if (reset) {
        const resetDate = new Date(parseInt(reset) * 1000);
        console.log(`   Resets at: ${resetDate.toLocaleString()}`);
      }

      // 残り10%を切ったら警告
      if (remaining / limit < 0.1) {
        console.warn(`⚠️  Rate limit almost exceeded! ${remaining} requests remaining.`);
      }
    }
  }

  /**
   * エラーハンドリング
   */
  private handleError(error: AxiosError<ErrorResponse>): void {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.message;

      switch (status) {
        case 401:
          console.error('🔐 Authentication required. Please login first.');
          break;
        case 403:
          console.error('🚫 Forbidden. Check your permissions.');
          break;
        case 404:
          console.error('🔍 Resource not found.');
          break;
        case 429:
          console.error('⏱️  Rate limit exceeded. Please wait and try again.');
          break;
        case 500:
          console.error('🔥 Server error:', detail);
          break;
        default:
          console.error(`❌ Error ${status}:`, detail);
      }
    } else if (error.request) {
      console.error('🌐 Network error: No response from server.');
    } else {
      console.error('❌ Request setup error:', error.message);
    }
  }
}

// =====================================
// 使用例
// =====================================

async function main() {
  const client = new LocalDBKitClient('http://localhost:8000/api/v1');

  try {
    // 1. ログイン
    await client.login('admin', 'admin');

    // 2. モデル一覧取得
    const models = await client.getModels();
    console.log('Available models:', models.map((m) => m.name).join(', '));

    // 3. チャット
    const chatResponse = await client.chat({
      prompt: 'Explain what LocalDBKit is in one sentence.',
      model: 'gemma2:9b',
    });
    console.log('Chat response:', chatResponse);

    // 4. RAGドキュメント追加
    await client.addDocument({
      content: 'LocalDBKit is a complete local database development kit with Docker Compose.',
      collection: 'test_collection',
      metadata: {
        category: 'documentation',
        language: 'en',
      },
    });

    // 5. RAGクエリ
    const ragResponse = await client.ragQuery({
      query: 'What is LocalDBKit?',
      collection: 'test_collection',
      use_llm: true,
      top_k: 3,
    });
    console.log('RAG answer:', ragResponse.answer);
    console.log('Sources:', ragResponse.sources.length);

    // 6. コレクション一覧
    const collections = await client.getCollections();
    console.log('Collections:', collections.collections.map((c) => c.name).join(', '));

  } catch (error) {
    console.error('Main error:', error);
  } finally {
    client.logout();
  }
}

// 実行
if (require.main === module) {
  main().catch(console.error);
}

// エクスポート（モジュールとして使用する場合）
export { LocalDBKitClient };
export type {
  AuthResponse,
  LLMModel,
  ModelsResponse,
  ChatRequest,
  ChatResponse,
  AddDocumentRequest,
  AddDocumentResponse,
  RAGQueryRequest,
  RAGQueryResponse,
  RAGSource,
  ErrorResponse,
  ImageUploadResponse,
  PDFUploadResponse,
  CollectionsResponse,
};
