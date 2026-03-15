"""
MongoDB の使用例 (Python)
pip install pymongo
"""

from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# 接続
client = MongoClient('mongodb://admin:admin@localhost:27017/')
db = client['mydb']

# コレクション取得
users_collection = db['users']
posts_collection = db['posts']

print("=== MongoDB 接続テスト ===")
print(f"データベース: {db.name}")

# 1. ドキュメントの挿入
print("\n=== ドキュメント挿入 ===")
user1 = {
    'name': 'Alice',
    'email': 'alice@example.com',
    'age': 28,
    'tags': ['developer', 'python'],
    'created_at': datetime.utcnow()
}

user2 = {
    'name': 'Bob',
    'email': 'bob@example.com',
    'age': 32,
    'tags': ['designer', 'ui/ux'],
    'address': {
        'city': 'Tokyo',
        'country': 'Japan'
    },
    'created_at': datetime.utcnow()
}

# 単一ドキュメント挿入
result1 = users_collection.insert_one(user1)
print(f"挿入されたID: {result1.inserted_id}")

# 複数ドキュメント挿入
users_to_insert = [
    user2,
    {
        'name': 'Charlie',
        'email': 'charlie@example.com',
        'age': 25,
        'tags': ['student'],
        'created_at': datetime.utcnow()
    }
]
result2 = users_collection.insert_many(users_to_insert)
print(f"挿入された数: {len(result2.inserted_ids)}")

# 2. ドキュメントの検索
print("\n=== ドキュメント検索 ===")

# 全ドキュメント取得
print(f"全ユーザー数: {users_collection.count_documents({})}")

# 条件検索
young_users = users_collection.find({'age': {'$lt': 30}})
print("30歳未満のユーザー:")
for user in young_users:
    print(f"  - {user['name']} ({user['age']}歳)")

# 単一ドキュメント取得
alice = users_collection.find_one({'name': 'Alice'})
print(f"\nAliceの情報: {alice}")

# 配列を含む検索
developers = users_collection.find({'tags': 'developer'})
print("\n開発者:")
for dev in developers:
    print(f"  - {dev['name']}")

# 3. ドキュメントの更新
print("\n=== ドキュメント更新 ===")

# 単一ドキュメント更新
users_collection.update_one(
    {'name': 'Alice'},
    {'$set': {'age': 29, 'updated_at': datetime.utcnow()}}
)
print("Aliceの年齢を更新しました")

# 配列に要素追加
users_collection.update_one(
    {'name': 'Alice'},
    {'$push': {'tags': 'javascript'}}
)

# 複数ドキュメント更新
result = users_collection.update_many(
    {},
    {'$set': {'status': 'active'}}
)
print(f"{result.modified_count}件のドキュメントを更新しました")

# 4. 集計パイプライン
print("\n=== 集計パイプライン ===")

# 年齢の統計
pipeline = [
    {
        '$group': {
            '_id': None,
            'average_age': {'$avg': '$age'},
            'min_age': {'$min': '$age'},
            'max_age': {'$max': '$age'},
            'total_users': {'$sum': 1}
        }
    }
]
result = list(users_collection.aggregate(pipeline))
if result:
    stats = result[0]
    print(f"ユーザー数: {stats['total_users']}")
    print(f"平均年齢: {stats['average_age']:.1f}歳")
    print(f"最年少: {stats['min_age']}歳")
    print(f"最年長: {stats['max_age']}歳")

# タグごとのユーザー数
tag_pipeline = [
    {'$unwind': '$tags'},
    {'$group': {'_id': '$tags', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
]
print("\nタグ別ユーザー数:")
for tag_stat in users_collection.aggregate(tag_pipeline):
    print(f"  - {tag_stat['_id']}: {tag_stat['count']}人")

# 5. インデックス作成
print("\n=== インデックス作成 ===")
users_collection.create_index('email', unique=True)
users_collection.create_index([('name', 1), ('age', -1)])
print("インデックスを作成しました")
print("インデックス一覧:")
for index in users_collection.list_indexes():
    print(f"  - {index['name']}")

# 6. リレーションシップ（参照）
print("\n=== ドキュメント間の参照 ===")

# 投稿を作成
alice_id = users_collection.find_one({'name': 'Alice'})['_id']
post = {
    'user_id': alice_id,  # ユーザーへの参照
    'title': 'MongoDBの使い方',
    'content': 'MongoDBは柔軟なドキュメントデータベースです',
    'likes': 0,
    'comments': [],
    'created_at': datetime.utcnow()
}
posts_collection.insert_one(post)

# Lookup（JOIN相当）
pipeline = [
    {
        '$lookup': {
            'from': 'users',
            'localField': 'user_id',
            'foreignField': '_id',
            'as': 'author'
        }
    },
    {'$unwind': '$author'},
    {'$project': {
        'title': 1,
        'author_name': '$author.name',
        'created_at': 1
    }}
]

print("投稿一覧（著者情報付き）:")
for post in posts_collection.aggregate(pipeline):
    print(f"  - '{post['title']}' by {post['author_name']}")

# 7. ドキュメント削除
print("\n=== ドキュメント削除 ===")
# 削除はコメントアウト
# users_collection.delete_one({'name': 'Charlie'})
# users_collection.delete_many({'age': {'$gte': 30}})
print("削除操作はスキップしました（コード内でコメントアウト解除可能）")

client.close()
print("\n完了!")
