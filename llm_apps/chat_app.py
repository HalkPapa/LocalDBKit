#!/usr/bin/env python3
"""
ローカルLLMチャットアプリ（Ollama + Streamlit）
作成者: Claude Sonnet 4.5 (Anthropic)
作成日: 2026年3月11日

このアプリは:
- Ollamaを使ったローカルLLMチャット
- 会話履歴をMongoDBに保存
- シンプルなWebUI（Streamlit）
"""

import streamlit as st
import ollama
from pymongo import MongoClient
from datetime import datetime
import json

# ページ設定
st.set_page_config(
    page_title="ローカルLLMチャット",
    page_icon="🤖",
    layout="wide"
)

# MongoDB接続
@st.cache_resource
def get_mongodb():
    client = MongoClient("mongodb://admin:admin@localhost:27017/?authSource=admin")
    return client["llm_chat"]

# Ollama利用可能確認
def check_ollama():
    try:
        ollama.list()
        return True
    except:
        return False

# モデル一覧取得
@st.cache_data(ttl=60)
def get_available_models():
    try:
        models = ollama.list()
        return [model['name'] for model in models.get('models', [])]
    except:
        return []

# チャット履歴保存
def save_chat_history(session_id, role, content, model):
    db = get_mongodb()
    db.chat_history.insert_one({
        "session_id": session_id,
        "role": role,
        "content": content,
        "model": model,
        "timestamp": datetime.now()
    })

# チャット履歴読み込み
def load_chat_history(session_id):
    db = get_mongodb()
    history = list(db.chat_history.find(
        {"session_id": session_id}
    ).sort("timestamp", 1))
    return history

# セッションID生成
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# サイドバー
with st.sidebar:
    st.title("🤖 ローカルLLMチャット")

    # Ollamaステータス
    ollama_available = check_ollama()
    if ollama_available:
        st.success("✅ Ollama接続OK")
    else:
        st.error("❌ Ollamaに接続できません")
        st.info("""
        Ollamaを起動してください:
        ```bash
        docker-compose up -d ollama
        ```
        """)
        st.stop()

    # モデル選択
    available_models = get_available_models()

    if not available_models:
        st.warning("⚠️ モデルがインストールされていません")
        st.info("""
        モデルをインストールしてください:
        ```bash
        docker exec -it local_ollama ollama pull llama3.2
        ```

        推奨モデル:
        - llama3.2 (3B, 軽量)
        - llama3.2:1b (1B, 超軽量)
        - gemma2:2b (2B, Google製)
        """)

        # デフォルトモデルを設定
        model = "llama3.2"
    else:
        model = st.selectbox(
            "モデル選択",
            available_models,
            index=0
        )

    st.divider()

    # セッション情報
    st.subheader("セッション情報")
    st.text(f"ID: {st.session_state.session_id}")
    st.text(f"メッセージ数: {len(st.session_state.messages)}")

    # 会話クリア
    if st.button("🗑️ 会話をクリア", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # システム情報
    st.subheader("システム情報")
    st.text(f"DB: MongoDB")
    st.text(f"LLM: Ollama")
    st.text(f"UI: Streamlit")

# メインエリア
st.title("💬 ローカルLLMチャット")
st.caption("完全にローカルで動作するプライベートなチャットシステム")

# 会話履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("メッセージを入力..."):
    # ユーザーメッセージ表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ユーザーメッセージ保存
    save_chat_history(st.session_state.session_id, "user", prompt, model)

    # アシスタント応答
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Ollamaでストリーミング生成
            stream = ollama.chat(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    full_response += chunk['message']['content']
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            message_placeholder.error(error_msg)
            full_response = error_msg

    # アシスタントメッセージ保存
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_chat_history(st.session_state.session_id, "assistant", full_response, model)

# フッター
st.divider()
st.caption("🔒 全てのデータはローカルで処理され、外部に送信されません")
