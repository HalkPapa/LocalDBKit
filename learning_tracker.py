"""
学習管理システム - データ収集・分析スクリプト
Open WebUI API から会話履歴を取得してMongoDBに保存
"""

import requests
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import List, Dict
import time

# ==============================
# 設定
# ==============================

OPEN_WEBUI_URL = "http://localhost:3000"
MONGODB_URL = "mongodb://admin:admin@localhost:27017/?authSource=admin"
DB_NAME = "learning_management"

# ==============================
# MongoDB接続
# ==============================

class LearningTracker:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DB_NAME]

        # コレクション
        self.sessions = self.db["learning_sessions"]
        self.messages = self.db["learning_messages"]
        self.topics = self.db["learning_topics"]
        self.goals = self.db["learning_goals"]
        self.stats = self.db["learning_stats"]

        print("✅ MongoDB接続完了")

    def create_indexes(self):
        """インデックス作成"""
        self.sessions.create_index("session_id")
        self.sessions.create_index("start_time")
        self.sessions.create_index("topic")
        self.messages.create_index("session_id")
        self.messages.create_index("timestamp")
        print("✅ インデックス作成完了")

    def record_session(self, session_data: Dict):
        """学習セッションを記録"""
        session = {
            "session_id": session_data.get("id"),
            "title": session_data.get("title", "Untitled"),
            "start_time": datetime.fromisoformat(session_data.get("created_at", datetime.now().isoformat())),
            "last_update": datetime.fromisoformat(session_data.get("updated_at", datetime.now().isoformat())),
            "model_used": session_data.get("model", "unknown"),
            "messages_count": len(session_data.get("messages", [])),
            "topic": self._extract_topic(session_data.get("title", "")),
            "tags": session_data.get("tags", []),
        }

        # 会話時間を計算
        messages = session_data.get("messages", [])
        if messages:
            duration = self._calculate_duration(messages)
            session["duration_minutes"] = duration

        # セッション保存
        self.sessions.update_one(
            {"session_id": session["session_id"]},
            {"$set": session},
            upsert=True
        )

        # メッセージ保存
        for msg in messages:
            self.record_message(session["session_id"], msg)

        return session

    def record_message(self, session_id: str, message: Dict):
        """メッセージを記録"""
        msg = {
            "session_id": session_id,
            "role": message.get("role"),
            "content": message.get("content", ""),
            "timestamp": datetime.fromtimestamp(message.get("timestamp", time.time())),
            "model": message.get("model"),
        }

        self.messages.update_one(
            {"session_id": session_id, "timestamp": msg["timestamp"]},
            {"$set": msg},
            upsert=True
        )

    def _extract_topic(self, title: str) -> str:
        """タイトルからトピックを抽出"""
        # 簡易的なトピック抽出（改善可能）
        keywords = {
            "python": ["python", "パイソン"],
            "database": ["database", "データベース", "sql", "mongodb"],
            "llm": ["llm", "ai", "機械学習", "深層学習"],
            "web": ["web", "http", "api", "サーバー"],
            "general": []
        }

        title_lower = title.lower()
        for topic, words in keywords.items():
            if any(word in title_lower for word in words):
                return topic

        return "general"

    def _calculate_duration(self, messages: List[Dict]) -> float:
        """会話時間を計算（分）"""
        if len(messages) < 2:
            return 0

        timestamps = [msg.get("timestamp", 0) for msg in messages]
        duration_seconds = max(timestamps) - min(timestamps)
        return duration_seconds / 60

    def get_daily_stats(self, date: datetime = None) -> Dict:
        """日次統計取得"""
        if date is None:
            date = datetime.now()

        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)

        sessions = list(self.sessions.find({
            "start_time": {"$gte": start_of_day, "$lt": end_of_day}
        }))

        total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
        total_messages = sum(s.get("messages_count", 0) for s in sessions)

        topics = {}
        for s in sessions:
            topic = s.get("topic", "general")
            topics[topic] = topics.get(topic, 0) + 1

        return {
            "date": date.strftime("%Y-%m-%d"),
            "sessions_count": len(sessions),
            "total_duration_minutes": total_duration,
            "total_messages": total_messages,
            "topics": topics
        }

    def get_weekly_stats(self, weeks_ago: int = 0) -> List[Dict]:
        """週次統計取得"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday() + weeks_ago * 7)

        weekly_stats = []
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            daily = self.get_daily_stats(day)
            weekly_stats.append(daily)

        return weekly_stats

    def get_topic_breakdown(self, days: int = 30) -> Dict:
        """トピック別学習時間"""
        start_date = datetime.now() - timedelta(days=days)

        sessions = list(self.sessions.find({
            "start_time": {"$gte": start_date}
        }))

        topic_stats = {}
        for s in sessions:
            topic = s.get("topic", "general")
            if topic not in topic_stats:
                topic_stats[topic] = {
                    "duration_minutes": 0,
                    "sessions_count": 0,
                    "messages_count": 0
                }

            topic_stats[topic]["duration_minutes"] += s.get("duration_minutes", 0)
            topic_stats[topic]["sessions_count"] += 1
            topic_stats[topic]["messages_count"] += s.get("messages_count", 0)

        return topic_stats

    def set_goal(self, goal_data: Dict):
        """学習目標設定"""
        goal = {
            "goal_id": goal_data.get("id", str(int(time.time()))),
            "title": goal_data.get("title"),
            "target_duration_minutes": goal_data.get("target_duration", 0),
            "target_sessions": goal_data.get("target_sessions", 0),
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=goal_data.get("duration_days", 30)),
            "status": "active"
        }

        self.goals.update_one(
            {"goal_id": goal["goal_id"]},
            {"$set": goal},
            upsert=True
        )

        return goal

    def check_goal_progress(self, goal_id: str) -> Dict:
        """目標達成率確認"""
        goal = self.goals.find_one({"goal_id": goal_id})
        if not goal:
            return None

        sessions = list(self.sessions.find({
            "start_time": {
                "$gte": goal["start_date"],
                "$lte": goal.get("end_date", datetime.now())
            }
        }))

        total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
        total_sessions = len(sessions)

        progress = {
            "goal": goal["title"],
            "duration_progress": {
                "current": total_duration,
                "target": goal.get("target_duration_minutes", 0),
                "percentage": (total_duration / goal.get("target_duration_minutes", 1)) * 100 if goal.get("target_duration_minutes") else 0
            },
            "sessions_progress": {
                "current": total_sessions,
                "target": goal.get("target_sessions", 0),
                "percentage": (total_sessions / goal.get("target_sessions", 1)) * 100 if goal.get("target_sessions") else 0
            },
            "status": goal["status"]
        }

        return progress

# ==============================
# Open WebUI API連携
# ==============================

def fetch_openwebui_chats(api_token: str = None) -> List[Dict]:
    """Open WebUIから会話履歴を取得"""
    # 注意: Open WebUI APIキーが必要
    # 実装はOpen WebUIのAPIドキュメント参照

    # サンプル実装（実際のAPIに合わせて調整）
    try:
        headers = {}
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

        # チャット一覧取得（実際のエンドポイントに合わせて変更）
        response = requests.get(
            f"{OPEN_WEBUI_URL}/api/v1/chats",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⚠️ Open WebUI API接続エラー: {e}")

    return []

# ==============================
# メイン処理
# ==============================

if __name__ == "__main__":
    print("🎓 学習管理システム - データ収集")
    print("=" * 50)

    # トラッカー初期化
    tracker = LearningTracker()
    tracker.create_indexes()

    # サンプルデータ投入（テスト用）
    print("\n📝 サンプルデータ投入...")

    sample_session = {
        "id": "session_001",
        "title": "Python学習 - リスト操作",
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "updated_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        "model": "gemma2:9b",
        "messages": [
            {
                "role": "user",
                "content": "Pythonのリストについて教えて",
                "timestamp": (datetime.now() - timedelta(hours=2)).timestamp()
            },
            {
                "role": "assistant",
                "content": "Pythonのリストは...",
                "timestamp": (datetime.now() - timedelta(hours=2, minutes=-5)).timestamp(),
                "model": "gemma2:9b"
            }
        ],
        "tags": ["python", "基礎"]
    }

    tracker.record_session(sample_session)
    print("✅ サンプルセッション記録完了")

    # 統計表示
    print("\n📊 本日の学習統計:")
    daily = tracker.get_daily_stats()
    print(json.dumps(daily, indent=2, ensure_ascii=False, default=str))

    # 目標設定サンプル
    print("\n🎯 学習目標設定...")
    goal = tracker.set_goal({
        "id": "goal_001",
        "title": "毎日1時間学習",
        "target_duration": 60,
        "target_sessions": 30,
        "duration_days": 30
    })
    print(f"✅ 目標設定完了: {goal['title']}")

    print("\n✅ 学習管理システム初期化完了！")
    print("📊 ダッシュボードで統計を確認できます")
