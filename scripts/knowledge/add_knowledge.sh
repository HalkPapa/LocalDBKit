#!/bin/bash
# 知識追加スクリプト

cd "$(dirname "$0")"

echo "📚 知識追加ツール"
echo "=" 50

# 引数チェック
if [ $# -eq 0 ]; then
    echo "使い方:"
    echo "  ./add_knowledge.sh <ファイルまたはフォルダ>"
    echo ""
    echo "例:"
    echo "  ./add_knowledge.sh ~/Documents/python_book.pdf"
    echo "  ./add_knowledge.sh ~/Documents/notes/*.md"
    echo "  ./add_knowledge.sh knowledge/python/"
    exit 1
fi

# ファイル/フォルダ処理
for item in "$@"; do
    if [ -f "$item" ]; then
        # ファイルの場合
        echo "📄 追加: $item"
        python3 rag_system.py add "$item"
    elif [ -d "$item" ]; then
        # フォルダの場合、全ファイルを追加
        echo "📁 フォルダ: $item"
        find "$item" -type f \( -name "*.pdf" -o -name "*.md" -o -name "*.txt" \) | while read file; do
            echo "📄 追加: $file"
            python3 rag_system.py add "$file"
        done
    else
        echo "⚠️ 見つかりません: $item"
    fi
done

echo ""
echo "✅ 完了"
echo ""
echo "📊 現在の知識ベース:"
python3 rag_system.py list
