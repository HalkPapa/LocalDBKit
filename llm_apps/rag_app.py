#!/usr/bin/env python3
"""
RAG（検索拡張生成）アプリ
作成者: Claude Sonnet 4.5 (Anthropic)
作成日: 2026年3月11日

このアプリは:
- 自分のドキュメントをQdrantに保存
- 質問に関連するドキュメントを検索
- Ollamaで回答生成
"""

import streamlit as st
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# ページ設定
st.set_page_config(
    page_title="RAGチャット",
    page_icon="📚",
    layout="wide"
)

# 埋め込みモデル
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# Qdrant接続
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(url="http://localhost:6333")

# コレクション作成
def ensure_collection():
    client = get_qdrant_client()
    collection_name = "rag_documents"

    try:
        client.get_collection(collection_name)
    except:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

    return collection_name

# ドキュメント追加
def add_document(text, metadata=None):
    client = get_qdrant_client()
    model = get_embedding_model()
    collection_name = ensure_collection()

    # 埋め込み生成
    vector = model.encode(text).tolist()

    # Qdrantに保存
    point_id = abs(hash(text)) % (10 ** 10)
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": text,
                    "metadata": metadata or {}
                }
            )
        ]
    )

    return point_id

# ドキュメント検索
def search_documents(query, top_k=3):
    client = get_qdrant_client()
    model = get_embedding_model()
    collection_name = ensure_collection()

    # クエリ埋め込み
    query_vector = model.encode(query).tolist()

    # 検索
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k
    ).points

    return results

# RAG応答生成
def generate_rag_response(query, model_name, context_docs):
    # コンテキスト構築
    context = "\n\n".join([
        f"【ドキュメント {i+1}】\n{doc.payload['text']}"
        for i, doc in enumerate(context_docs)
    ])

    # プロンプト構築
    prompt = f"""以下のドキュメントを参考にして、質問に答えてください。

## 参考ドキュメント
{context}

## 質問
{query}

## 回答
参考ドキュメントの内容に基づいて、正確に答えてください。"""

    # Ollamaで生成
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response['message']['content']

# セッション状態初期化
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

# サイドバー
with st.sidebar:
    st.title("📚 RAGチャット")
    st.caption("ドキュメント検索＋LLM")

    st.divider()

    # モデル選択
    try:
        models = ollama.list()
        available_models = [m['name'] for m in models.get('models', [])]

        if available_models:
            model = st.selectbox("モデル選択", available_models)
        else:
            st.warning("モデルがありません")
            model = "llama3.2"
    except:
        st.error("Ollamaに接続できません")
        st.stop()

    st.divider()

    # ドキュメント追加
    st.subheader("📄 ドキュメント追加")

    with st.form("add_document"):
        doc_text = st.text_area(
            "ドキュメントテキスト",
            height=150,
            placeholder="学習させたいテキストを入力..."
        )

        doc_title = st.text_input(
            "タイトル（オプション）",
            placeholder="例: プロジェクト概要"
        )

        if st.form_submit_button("📝 追加", use_container_width=True):
            if doc_text:
                with st.spinner("追加中..."):
                    point_id = add_document(
                        doc_text,
                        {"title": doc_title}
                    )
                st.success(f"✅ 追加完了 (ID: {point_id})")
            else:
                st.error("テキストを入力してください")

    st.divider()

    # 統計情報
    st.subheader("📊 統計")
    try:
        client = get_qdrant_client()
        collection_name = ensure_collection()
        info = client.get_collection(collection_name)
        st.metric("ドキュメント数", info.points_count)
    except:
        st.metric("ドキュメント数", 0)

    # クリア
    if st.button("🗑️ 会話クリア", use_container_width=True):
        st.session_state.rag_messages = []
        st.rerun()

# メインエリア
st.title("💬 RAGチャット")
st.caption("あなたのドキュメントを学習したAIアシスタント")

# タブ
tab1, tab2 = st.tabs(["💬 チャット", "🔍 検索テスト"])

with tab1:
    # 会話履歴表示
    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # 参考ドキュメント表示
            if "sources" in message:
                with st.expander("📚 参考ドキュメント"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"""
                        **ドキュメント {i+1}** (類似度: {source['score']:.3f})
                        ```
                        {source['text'][:200]}...
                        ```
                        """)

    # ユーザー入力
    if prompt := st.chat_input("質問を入力..."):
        # ユーザーメッセージ表示
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 検索＋生成
        with st.chat_message("assistant"):
            with st.spinner("🔍 関連ドキュメントを検索中..."):
                docs = search_documents(prompt, top_k=3)

            if not docs:
                response = "申し訳ありません。関連するドキュメントが見つかりませんでした。まずドキュメントを追加してください。"
            else:
                with st.spinner("💭 回答を生成中..."):
                    response = generate_rag_response(prompt, model, docs)

            st.markdown(response)

            # 参考ドキュメント表示
            if docs:
                with st.expander("📚 参考ドキュメント"):
                    for i, doc in enumerate(docs):
                        st.markdown(f"""
                        **ドキュメント {i+1}** (類似度: {doc.score:.3f})
                        ```
                        {doc.payload['text'][:200]}...
                        ```
                        """)

        # アシスタントメッセージ保存
        st.session_state.rag_messages.append({
            "role": "assistant",
            "content": response,
            "sources": [
                {
                    "text": doc.payload['text'],
                    "score": doc.score
                }
                for doc in docs
            ] if docs else []
        })

with tab2:
    st.subheader("🔍 検索テスト")
    st.caption("LLMを使わず、ドキュメント検索だけをテスト")

    search_query = st.text_input(
        "検索クエリ",
        placeholder="例: データベースの使い方"
    )

    top_k = st.slider("取得件数", 1, 10, 3)

    if st.button("🔍 検索", use_container_width=True):
        if search_query:
            with st.spinner("検索中..."):
                results = search_documents(search_query, top_k=top_k)

            if results:
                st.success(f"✅ {len(results)}件見つかりました")

                for i, result in enumerate(results):
                    with st.expander(f"📄 結果 {i+1} (類似度: {result.score:.3f})"):
                        st.markdown(f"**テキスト:**\n{result.payload['text']}")
                        if result.payload.get('metadata', {}).get('title'):
                            st.markdown(f"**タイトル:** {result.payload['metadata']['title']}")
            else:
                st.warning("結果が見つかりませんでした")
        else:
            st.error("検索クエリを入力してください")

# フッター
st.divider()
st.caption("🔒 全データローカル保存 | 📚 RAG (Retrieval-Augmented Generation)")
