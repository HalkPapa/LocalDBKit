.PHONY: help up down restart logs health clean install test

help: ## このヘルプを表示
	@echo "LocalDBKit - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## 全サービスを起動
	docker compose up -d
	@echo "✅ 全サービスが起動しました"
	@echo "💡 'make health' でヘルスチェックを実行できます"

down: ## 全サービスを停止
	docker compose down
	@echo "✅ 全サービスが停止しました"

restart: ## 全サービスを再起動
	docker compose restart
	@echo "✅ 全サービスが再起動しました"

logs: ## ログを表示（リアルタイム）
	docker compose logs -f

logs-app: ## アプリケーションログのみ表示
	docker compose logs -f ollama open-webui

health: ## ヘルスチェック実行
	@./scripts/deployment/health-check.sh

ps: ## コンテナ状態を表示
	docker compose ps

clean: ## 停止してボリュームも削除（データ削除注意！）
	@echo "⚠️  警告: 全てのデータが削除されます"
	@read -p "続行しますか？ (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v
	@echo "✅ 全データが削除されました"

install: ## Python依存関係をインストール
	pip3 install -r requirements.txt
	@echo "✅ Python依存関係がインストールされました"

# RAG関連
rag-api: ## RAG APIを起動
	python3 apps/rag/rag_api.py

add-knowledge: ## 知識を追加（例: make add-knowledge FILE=path/to/file.pdf）
	@if [ -z "$(FILE)" ]; then \
		echo "エラー: FILEパラメータが必要です"; \
		echo "使用例: make add-knowledge FILE=path/to/file.pdf"; \
		exit 1; \
	fi
	./scripts/knowledge/add_knowledge.sh $(FILE)

list-knowledge: ## 登録済み知識を一覧表示
	python3 apps/rag/rag_system.py list

# ダッシュボード関連
dashboard-llm: ## LLMダッシュボード起動（port 8501）
	streamlit run apps/dashboard/llm_dashboard.py --server.port 8501

dashboard-learning: ## 学習ダッシュボード起動（port 8502）
	streamlit run apps/learning/learning_dashboard.py --server.port 8502

# 開発用
dev: up install ## 開発環境セットアップ
	@echo "✅ 開発環境の準備が完了しました"
	@echo ""
	@echo "次のステップ:"
	@echo "  1. make rag-api          # RAG APIを起動"
	@echo "  2. make dashboard-llm    # ダッシュボードを起動"
	@echo "  3. Open http://localhost:3000  # Open WebUIにアクセス"

# バックアップ
backup: ## データベースをバックアップ
	./scripts/deployment/backup.sh

restore: ## バックアップからリストア（例: make restore BACKUP=./backups/20260315_120000）
	@if [ -z "$(BACKUP)" ]; then \
		echo "エラー: BACKUPパラメータが必要です"; \
		echo "使用例: make restore BACKUP=./backups/20260315_120000"; \
		exit 1; \
	fi
	./scripts/deployment/restore.sh $(BACKUP)
