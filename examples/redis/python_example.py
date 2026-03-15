"""
Redis の使用例 (Python)
pip install redis
"""

import redis
import json
import time

# 接続
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 接続確認
print("=== Redis 接続テスト ===")
print(f"Ping: {r.ping()}")

# 1. 基本的なキー・バリュー操作
print("\n=== Key-Value 操作 ===")
r.set('user:1:name', 'Alice')
r.set('user:1:email', 'alice@example.com')
print(f"Name: {r.get('user:1:name')}")
print(f"Email: {r.get('user:1:email')}")

# TTL付きで保存（セッション管理など）
r.setex('session:abc123', 3600, 'user_id:1')  # 1時間で期限切れ
print(f"Session TTL: {r.ttl('session:abc123')}秒")

# 2. ハッシュ（オブジェクト保存）
print("\n=== Hash 操作 ===")
user_data = {
    'name': 'Bob',
    'email': 'bob@example.com',
    'age': '30',
    'city': 'Tokyo'
}
r.hset('user:2', mapping=user_data)
print(f"User 2: {r.hgetall('user:2')}")

# 3. リスト（キュー、スタック）
print("\n=== List 操作 ===")
# キューとして使用
r.lpush('queue:tasks', 'task1', 'task2', 'task3')
task = r.rpop('queue:tasks')
print(f"処理中のタスク: {task}")
print(f"残りのタスク: {r.lrange('queue:tasks', 0, -1)}")

# 4. セット（ユニークな値の集合）
print("\n=== Set 操作 ===")
r.sadd('tags:post1', 'python', 'redis', 'database')
r.sadd('tags:post2', 'python', 'django', 'web')
print(f"Post1 のタグ: {r.smembers('tags:post1')}")
print(f"共通タグ: {r.sinter('tags:post1', 'tags:post2')}")

# 5. ソート済みセット（ランキング、スコアボード）
print("\n=== Sorted Set 操作 ===")
r.zadd('leaderboard', {'player1': 100, 'player2': 250, 'player3': 180})
print("リーダーボード（上位3位）:")
top_players = r.zrevrange('leaderboard', 0, 2, withscores=True)
for rank, (player, score) in enumerate(top_players, 1):
    print(f"  {rank}. {player}: {int(score)}点")

# 6. Pub/Sub（リアルタイム通知）
print("\n=== Pub/Sub 例 ===")
print("メッセージを配信...")
r.publish('notifications', json.dumps({
    'type': 'new_message',
    'user': 'Alice',
    'message': 'Hello!'
}))

# 7. キャッシュパターン
print("\n=== キャッシュパターン ===")
def get_user_profile(user_id):
    # キャッシュをチェック
    cache_key = f'cache:user:{user_id}'
    cached = r.get(cache_key)

    if cached:
        print(f"キャッシュヒット: {cache_key}")
        return json.loads(cached)

    # キャッシュミス - DBから取得（シミュレーション）
    print(f"キャッシュミス - DBから取得")
    profile = {
        'id': user_id,
        'name': 'User ' + str(user_id),
        'created_at': time.time()
    }

    # キャッシュに保存（5分間）
    r.setex(cache_key, 300, json.dumps(profile))
    return profile

profile1 = get_user_profile(123)
profile2 = get_user_profile(123)  # キャッシュヒット

# 8. カウンター（ページビュー、いいね数など）
print("\n=== カウンター ===")
r.incr('page:home:views')
r.incrby('page:home:views', 5)
print(f"ページビュー: {r.get('page:home:views')}")

print("\n完了!")
