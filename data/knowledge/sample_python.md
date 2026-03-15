# Pythonプログラミングガイド

## リスト操作

Pythonのリストは、順序付きで変更可能なコレクションです。

### 基本操作

```python
# リスト作成
my_list = [1, 2, 3, 4, 5]

# 要素追加
my_list.append(6)

# 要素削除
my_list.remove(3)

# リスト内包表記
squared = [x**2 for x in range(10)]
```

### ベストプラクティス

1. **リスト内包表記を使う** - ループより高速で読みやすい
2. **適切なデータ構造を選ぶ** - 固定ならタプル、重複なしならセット
3. **スライスを活用** - `list[:]`でコピー、`list[::2]`で偶数インデックス

## 辞書操作

辞書は、キーと値のペアを格納します。

### 基本操作

```python
# 辞書作成
my_dict = {"name": "Alice", "age": 30}

# 値の取得
name = my_dict.get("name", "Unknown")

# キーの存在確認
if "age" in my_dict:
    print(my_dict["age"])
```

### ベストプラクティス

1. **get()メソッドを使う** - KeyErrorを避ける
2. **defaultdictを活用** - 初期値の設定が簡単
3. **辞書内包表記** - `{k: v for k, v in items}`

## 関数定義

### タイプヒント

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

タイプヒントを使うことで、コードの可読性と保守性が向上します。

### デコレータ

```python
from functools import wraps

def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_function
def my_function():
    pass
```

## エラーハンドリング

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    cleanup()
```

### ベストプラクティス

1. **具体的な例外をキャッチ** - `Exception`は最後の手段
2. **finallyブロックを使う** - リソースの確実なクリーンアップ
3. **カスタム例外を作成** - 明確なエラーメッセージ
