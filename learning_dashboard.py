"""
統合学習管理ダッシュボード
LLM評価 + 学習統計を統合表示
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from learning_tracker import LearningTracker
import sys

# ページ設定
st.set_page_config(
    page_title="学習管理ダッシュボード",
    page_icon="📚",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
.big-metric {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
}
.goal-progress {
    background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# タイトル
st.title("📚 統合学習管理ダッシュボード")
st.markdown("**LLMモデル評価 + 学習進捗管理**")
st.markdown("---")

# サイドバー
st.sidebar.header("⚙️ 設定")
page = st.sidebar.radio(
    "ページ選択",
    ["📊 学習統計", "🎯 目標管理", "🤖 モデル評価", "📈 詳細分析"]
)

refresh_button = st.sidebar.button("🔄 データ更新")

# LearningTracker初期化
try:
    tracker = LearningTracker()
except Exception as e:
    st.error(f"MongoDB接続エラー: {e}")
    st.stop()

# ==============================
# ページ1: 学習統計
# ==============================

if page == "📊 学習統計":
    st.header("📊 学習統計ダッシュボード")

    # 期間選択
    col1, col2 = st.columns([2, 1])
    with col1:
        period = st.selectbox(
            "表示期間",
            ["今日", "今週", "今月", "全期間"]
        )

    # 本日の統計
    st.subheader("📅 本日の学習")

    daily_stats = tracker.get_daily_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "学習セッション数",
            f"{daily_stats['sessions_count']} 回",
            delta=None
        )

    with col2:
        st.metric(
            "総学習時間",
            f"{daily_stats['total_duration_minutes']:.1f} 分",
            delta=None
        )

    with col3:
        st.metric(
            "メッセージ数",
            f"{daily_stats['total_messages']} 件",
            delta=None
        )

    with col4:
        avg_duration = daily_stats['total_duration_minutes'] / max(daily_stats['sessions_count'], 1)
        st.metric(
            "平均セッション時間",
            f"{avg_duration:.1f} 分",
            delta=None
        )

    st.markdown("---")

    # 週次統計
    st.subheader("📈 週次学習推移")

    weekly_stats = tracker.get_weekly_stats()
    df_weekly = pd.DataFrame(weekly_stats)

    # 学習時間グラフ
    fig_weekly = go.Figure()

    fig_weekly.add_trace(go.Bar(
        x=df_weekly['date'],
        y=df_weekly['total_duration_minutes'],
        name='学習時間',
        marker_color='#4CAF50',
        hovertemplate='<b>%{x}</b><br>学習時間: %{y:.1f}分<extra></extra>'
    ))

    fig_weekly.update_layout(
        title="日別学習時間",
        xaxis_title="日付",
        yaxis_title="学習時間 (分)",
        hovermode="x unified",
        height=400
    )

    st.plotly_chart(fig_weekly, use_container_width=True)

    # セッション数グラフ
    fig_sessions = go.Figure()

    fig_sessions.add_trace(go.Scatter(
        x=df_weekly['date'],
        y=df_weekly['sessions_count'],
        mode='lines+markers',
        name='セッション数',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>セッション: %{y}回<extra></extra>'
    ))

    fig_sessions.update_layout(
        title="日別セッション数",
        xaxis_title="日付",
        yaxis_title="セッション数",
        hovermode="x unified",
        height=400
    )

    st.plotly_chart(fig_sessions, use_container_width=True)

    st.markdown("---")

    # トピック別学習時間
    st.subheader("📚 トピック別学習時間（過去30日）")

    topic_stats = tracker.get_topic_breakdown(days=30)

    if topic_stats:
        df_topics = pd.DataFrame([
            {
                "トピック": topic,
                "学習時間(分)": data["duration_minutes"],
                "セッション数": data["sessions_count"],
                "メッセージ数": data["messages_count"]
            }
            for topic, data in topic_stats.items()
        ])

        # 円グラフ
        fig_topics = px.pie(
            df_topics,
            values='学習時間(分)',
            names='トピック',
            title='トピック別学習時間分布',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig_topics.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>学習時間: %{value:.1f}分<br>割合: %{percent}<extra></extra>'
        )

        st.plotly_chart(fig_topics, use_container_width=True)

        # テーブル表示
        st.dataframe(
            df_topics.sort_values('学習時間(分)', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("まだ学習データがありません。学習を開始してください！")

# ==============================
# ページ2: 目標管理
# ==============================

elif page == "🎯 目標管理":
    st.header("🎯 学習目標管理")

    # 新しい目標設定
    with st.expander("➕ 新しい目標を設定"):
        goal_title = st.text_input("目標タイトル", "毎日1時間学習")

        col1, col2 = st.columns(2)
        with col1:
            target_duration = st.number_input("目標時間（分）", min_value=0, value=60)
        with col2:
            target_sessions = st.number_input("目標セッション数", min_value=0, value=30)

        duration_days = st.slider("期間（日）", min_value=1, max_value=90, value=30)

        if st.button("🎯 目標を設定"):
            goal = tracker.set_goal({
                "title": goal_title,
                "target_duration": target_duration,
                "target_sessions": target_sessions,
                "duration_days": duration_days
            })
            st.success(f"✅ 目標を設定しました: {goal['title']}")

    st.markdown("---")

    # アクティブな目標一覧
    st.subheader("📋 アクティブな目標")

    active_goals = list(tracker.goals.find({"status": "active"}))

    if active_goals:
        for goal in active_goals:
            progress = tracker.check_goal_progress(goal["goal_id"])

            if progress:
                st.markdown(f"### {progress['goal']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**学習時間の進捗**")
                    duration_pct = min(progress["duration_progress"]["percentage"], 100)
                    st.progress(duration_pct / 100)
                    st.write(f"{progress['duration_progress']['current']:.1f} / {progress['duration_progress']['target']} 分 ({duration_pct:.1f}%)")

                with col2:
                    st.write("**セッション数の進捗**")
                    sessions_pct = min(progress["sessions_progress"]["percentage"], 100)
                    st.progress(sessions_pct / 100)
                    st.write(f"{progress['sessions_progress']['current']} / {progress['sessions_progress']['target']} セッション ({sessions_pct:.1f}%)")

                # 達成状況
                if duration_pct >= 100 and sessions_pct >= 100:
                    st.success("🎉 目標達成！おめでとうございます！")
                elif duration_pct >= 50 or sessions_pct >= 50:
                    st.info("💪 順調です！この調子で続けましょう！")
                else:
                    st.warning("📈 もう少し頑張りましょう！")

                st.markdown("---")
    else:
        st.info("まだ目標が設定されていません。新しい目標を設定してください！")

# ==============================
# ページ3: モデル評価
# ==============================

elif page == "🤖 モデル評価":
    st.header("🤖 LLMモデル評価")

    # 既存のLLM評価ダッシュボードの内容を統合
    st.info("LLMモデルの評価結果を表示（既存のllm_dashboard.pyの内容を統合）")

    # llm_dashboard.pyの内容をインポートして表示
    # または、評価結果を直接読み込んで表示

# ==============================
# ページ4: 詳細分析
# ==============================

elif page == "📈 詳細分析":
    st.header("📈 詳細分析")

    st.subheader("🔍 学習パターン分析")

    # 曜日別学習時間
    st.write("**曜日別学習パターン**")

    # 時間帯別学習
    st.write("**時間帯別学習パターン**")

    # 学習効率分析
    st.write("**学習効率分析**")
    st.info("メッセージあたりの学習時間、集中度など")

# フッター
st.markdown("---")
st.caption("💙 統合学習管理ダッシュボード - Powered by Streamlit & MongoDB")
