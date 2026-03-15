"""
LLMモデル評価ダッシュボード
Streamlit を使用したインタラクティブな分析ツール
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
from pathlib import Path
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="LLM Model Dashboard",
    page_icon="🤖",
    layout="wide"
)

# タイトル
st.title("🤖 LLMモデル評価ダッシュボード")
st.markdown("---")

# サイドバー
st.sidebar.header("⚙️ 設定")
refresh_button = st.sidebar.button("🔄 データ更新")

# Ollama API URL
OLLAMA_API_URL = "http://localhost:11434/api"

# 評価結果ファイルパス
EVAL_DIR = Path("/Users/koikedaisuke/MyProjects/personal agent/Docs/MultiModelLLM/evaluation")

# ==============================
# データ読み込み
# ==============================

@st.cache_data(ttl=60)
def load_evaluation_results():
    """評価結果JSONファイルを読み込む"""
    results = {}

    eval_files = {
        "Gemma2:9b": EVAL_DIR / "ollama_evaluation_results_gemma2_9b.json",
        "Qwen2.5:7b": EVAL_DIR / "ollama_evaluation_results_qwen2.5_7b.json",
        "Qwen2.5:14b": EVAL_DIR / "ollama_evaluation_results_qwen2.5_14b.json",
    }

    for model_name, file_path in eval_files.items():
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                results[model_name] = json.load(f)

    return results

@st.cache_data(ttl=60)
def get_ollama_models():
    """Ollamaから現在のモデル一覧を取得"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags", timeout=5)
        if response.status_code == 200:
            return response.json().get("models", [])
    except Exception as e:
        st.sidebar.error(f"Ollama接続エラー: {e}")
    return []

# データ読み込み
eval_results = load_evaluation_results()
ollama_models = get_ollama_models()

# ==============================
# 概要セクション
# ==============================

st.header("📊 モデル概要")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("評価済みモデル", len(eval_results))

with col2:
    st.metric("インストール済みモデル", len(ollama_models))

with col3:
    if eval_results:
        latest_eval = max(eval_results.values(), key=lambda x: x.get("timestamp", ""))
        st.metric("最終評価日時", latest_eval.get("timestamp", "N/A"))

st.markdown("---")

# ==============================
# モデル比較表
# ==============================

st.header("🏆 モデル比較")

if eval_results:
    comparison_data = []

    for model_name, result in eval_results.items():
        tests = result.get("tests", [])

        # スコア抽出
        japanese_score = 0
        persona_score = 0
        avg_response_time = 0

        for test in tests:
            if test["test_name"] == "日本語応答品質":
                japanese_score = test.get("avg_score", 0)
                avg_response_time = test.get("avg_response_time", 0)
            elif test["test_name"] == "静香ペルソナ再現性":
                persona_score = test.get("avg_score", 0)

        total_score = (japanese_score + persona_score) / 2

        # サイズ取得
        model_size = "N/A"
        for ollama_model in ollama_models:
            if model_name.lower().replace(":", "_") in ollama_model["name"].lower().replace(":", "_"):
                model_size = f"{ollama_model['size'] / 1e9:.1f} GB"
                break

        comparison_data.append({
            "モデル": model_name,
            "サイズ": model_size,
            "日本語品質": f"{japanese_score:.1f}%",
            "ペルソナ適合度": f"{persona_score:.1f}%",
            "総合スコア": f"{total_score:.1f}%",
            "平均応答時間": f"{avg_response_time:.2f}秒",
        })

    df_comparison = pd.DataFrame(comparison_data)

    # スタイル適用
    def highlight_max(s):
        is_max = s == s.max()
        return ['background-color: #90EE90' if v else '' for v in is_max]

    st.dataframe(
        df_comparison,
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("評価結果が見つかりません。")

st.markdown("---")

# ==============================
# 詳細スコアグラフ
# ==============================

st.header("📈 詳細評価スコア")

if eval_results:
    # データ準備
    score_data = []

    for model_name, result in eval_results.items():
        tests = result.get("tests", [])

        for test in tests:
            if test["test_name"] in ["日本語応答品質", "静香ペルソナ再現性"]:
                score_data.append({
                    "モデル": model_name,
                    "カテゴリ": test["test_name"],
                    "スコア": test.get("avg_score", 0)
                })

    df_scores = pd.DataFrame(score_data)

    # グラフ作成
    fig_scores = px.bar(
        df_scores,
        x="モデル",
        y="スコア",
        color="カテゴリ",
        barmode="group",
        title="評価スコア比較",
        color_discrete_map={
            "日本語応答品質": "#1f77b4",
            "静香ペルソナ再現性": "#ff7f0e"
        }
    )

    fig_scores.update_layout(
        yaxis_title="スコア (%)",
        xaxis_title="モデル",
        legend_title="評価項目",
        hovermode="x unified"
    )

    st.plotly_chart(fig_scores, use_container_width=True)

st.markdown("---")

# ==============================
# 応答時間比較
# ==============================

st.header("⚡ パフォーマンス比較")

col1, col2 = st.columns(2)

with col1:
    st.subheader("平均応答時間")

    if eval_results:
        response_time_data = []

        for model_name, result in eval_results.items():
            tests = result.get("tests", [])

            for test in tests:
                if test["test_name"] == "日本語応答品質":
                    response_time_data.append({
                        "モデル": model_name,
                        "応答時間(秒)": test.get("avg_response_time", 0)
                    })

        df_response_time = pd.DataFrame(response_time_data)

        fig_response = px.bar(
            df_response_time,
            x="モデル",
            y="応答時間(秒)",
            title="平均応答時間の比較",
            color="応答時間(秒)",
            color_continuous_scale="Reds"
        )

        fig_response.update_layout(
            yaxis_title="応答時間 (秒)",
            xaxis_title="モデル"
        )

        st.plotly_chart(fig_response, use_container_width=True)

with col2:
    st.subheader("生成速度")

    if eval_results:
        speed_data = []

        for model_name, result in eval_results.items():
            tests = result.get("tests", [])

            for test in tests:
                if test["test_name"] == "パフォーマンス":
                    speed_data.append({
                        "モデル": model_name,
                        "文字/秒": test.get("avg_chars_per_second", 0)
                    })

        df_speed = pd.DataFrame(speed_data)

        fig_speed = px.bar(
            df_speed,
            x="モデル",
            y="文字/秒",
            title="生成速度の比較",
            color="文字/秒",
            color_continuous_scale="Greens"
        )

        fig_speed.update_layout(
            yaxis_title="生成速度 (文字/秒)",
            xaxis_title="モデル"
        )

        st.plotly_chart(fig_speed, use_container_width=True)

st.markdown("---")

# ==============================
# 詳細データ
# ==============================

st.header("📋 詳細データ")

if eval_results:
    selected_model = st.selectbox(
        "モデル選択",
        list(eval_results.keys())
    )

    if selected_model:
        result = eval_results[selected_model]

        # タブ作成
        tab1, tab2, tab3 = st.tabs(["日本語品質", "ペルソナ再現性", "パフォーマンス"])

        with tab1:
            st.subheader("日本語応答品質テスト結果")

            for test in result.get("tests", []):
                if test["test_name"] == "日本語応答品質":
                    for i, test_result in enumerate(test["results"], 1):
                        with st.expander(f"テスト {i}: {test_result['test']}"):
                            st.write(f"**プロンプト:** {test_result['prompt']}")
                            st.write(f"**応答時間:** {test_result['elapsed_seconds']:.2f}秒")
                            st.write(f"**スコア:** {test_result['score']:.1f}%")
                            st.write(f"**応答:**")
                            st.info(test_result['response'])

        with tab2:
            st.subheader("静香ペルソナ再現性テスト結果")

            for test in result.get("tests", []):
                if test["test_name"] == "静香ペルソナ再現性":
                    for i, test_result in enumerate(test["results"], 1):
                        with st.expander(f"テスト {i}: {test_result['test']}"):
                            st.write(f"**プロンプト:** {test_result['prompt']}")
                            st.write(f"**応答時間:** {test_result['elapsed_seconds']:.2f}秒")
                            st.write(f"**スコア:** {test_result['score']:.1f}%")

                            # ペルソナチェック
                            checks = test_result.get("persona_checks", {})
                            cols = st.columns(4)
                            for idx, (key, value) in enumerate(checks.items()):
                                with cols[idx % 4]:
                                    icon = "✅" if value else "❌"
                                    st.write(f"{icon} {key}")

                            st.write(f"**応答:**")
                            st.success(test_result['response'])

        with tab3:
            st.subheader("パフォーマンステスト結果")

            for test in result.get("tests", []):
                if test["test_name"] == "パフォーマンス":
                    perf_data = []
                    for test_result in test["results"]:
                        perf_data.append({
                            "テスト": test_result["test"],
                            "応答時間(秒)": f"{test_result['elapsed_seconds']:.2f}",
                            "応答長(文字)": test_result["response_length"],
                            "生成速度(文字/秒)": f"{test_result['chars_per_second']:.2f}"
                        })

                    df_perf = pd.DataFrame(perf_data)
                    st.dataframe(df_perf, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================
# インストール済みモデル一覧
# ==============================

st.header("💾 インストール済みモデル（Ollama）")

if ollama_models:
    model_list = []

    for model in ollama_models:
        model_list.append({
            "モデル名": model["name"],
            "サイズ": f"{model['size'] / 1e9:.2f} GB",
            "更新日時": model.get("modified_at", "N/A")
        })

    df_models = pd.DataFrame(model_list)
    st.dataframe(df_models, use_container_width=True, hide_index=True)
else:
    st.warning("Ollamaに接続できません。")

# フッター
st.markdown("---")
st.caption("💙 LLMモデル評価ダッシュボード - Powered by Streamlit")
