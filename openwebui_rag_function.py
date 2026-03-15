"""
Open WebUI Function - RAG Knowledge Search
このファイルをOpen WebUIの「Functions」にインポートして使用
"""

import requests
import json
from typing import Optional

class Tools:
    """
    Open WebUI Function: RAG知識検索

    質問時に自動的に知識ベースを検索し、関連情報をLLMに提供します。
    """

    def __init__(self):
        self.citation = True

    class Valves:
        """設定"""
        RAG_API_URL: str = "http://host.docker.internal:8003/search"
        TOP_K: int = 3
        MIN_SCORE: float = 0.5
        ENABLE_AUTO_SEARCH: bool = True

    def __init__(self):
        self.valves = self.Valves()

    async def search_knowledge(
        self,
        query: str,
        __user__: Optional[dict] = None,
        __event_emitter__=None
    ) -> str:
        """
        知識ベースを検索

        :param query: 検索クエリ
        :return: 検索結果のコンテキスト
        """

        try:
            # RAG API呼び出し
            response = requests.post(
                self.valves.RAG_API_URL,
                json={
                    "query": query,
                    "top_k": self.valves.TOP_K
                },
                timeout=10
            )

            if response.status_code == 200:
                results = response.json()

                # スコアフィルタリング
                filtered = [
                    r for r in results
                    if r.get("score", 0) >= self.valves.MIN_SCORE
                ]

                if not filtered:
                    return ""

                # コンテキスト生成
                context_parts = ["[知識ベースからの参照情報]\n"]

                for i, item in enumerate(filtered, 1):
                    context_parts.append(
                        f"\n【参照 {i}】({item.get('filename', 'unknown')})\n"
                        f"{item.get('text', '')}\n"
                    )

                context_parts.append(
                    "\n上記の知識を参考にして、正確に回答してください。\n"
                    "知識に記載されていない内容は推測せず、「知識ベースにありません」と答えてください。\n"
                )

                # イベント送信（進捗表示）
                if __event_emitter__:
                    await __event_emitter__({
                        "type": "status",
                        "data": {
                            "description": f"知識ベースから{len(filtered)}件の参照情報を取得",
                            "done": True
                        }
                    })

                return "\n".join(context_parts)

        except Exception as e:
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"知識検索エラー: {str(e)}",
                        "done": True
                    }
                })

            return ""

        return ""

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__=None
    ) -> dict:
        """
        メインパイプライン
        全てのメッセージに対して自動的に知識検索を実行
        """

        # 自動検索が有効な場合のみ
        if not self.valves.ENABLE_AUTO_SEARCH:
            return body

        # 最新のユーザーメッセージを取得
        messages = body.get("messages", [])
        if not messages:
            return body

        last_message = messages[-1]
        if last_message.get("role") != "user":
            return body

        user_query = last_message.get("content", "")

        # 知識検索
        context = await self.search_knowledge(
            user_query,
            __user__=__user__,
            __event_emitter__=__event_emitter__
        )

        # コンテキストがあれば、システムメッセージに追加
        if context:
            # システムメッセージを探す
            system_message = None
            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg
                    break

            if system_message:
                # 既存のシステムメッセージに追加
                system_message["content"] = f"{context}\n\n{system_message['content']}"
            else:
                # 新しいシステムメッセージを挿入
                messages.insert(0, {
                    "role": "system",
                    "content": context
                })

        return body
