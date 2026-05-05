# Watchpoint — root Makefile
# Targets: dev, test, lint, seed, clean

UV   := /Users/sagarpatel/.local/bin/uv
BUN  := /Users/sagarpatel/.bun/bin/bun
DOCKER := /Applications/Docker.app/Contents/Resources/bin/docker

.PHONY: dev test lint seed clean

# ── Local dev stack ────────────────────────────────────────────────────────

dev:
	$(DOCKER) compose -f deploy/docker-compose/docker-compose.yml up -d

# ── Tests ──────────────────────────────────────────────────────────────────

test: test-api test-model-collector

test-api:
	@echo "▶ api tests"
	cd apps/api && $(UV) run --extra dev pytest -q

test-model-collector:
	@echo "▶ model-collector tests"
	cd agents/model-collector && $(UV) run --extra dev pytest -q

# ── Lint ───────────────────────────────────────────────────────────────────

lint: lint-api lint-model-collector lint-web

lint-api:
	@echo "▶ lint api"
	cd apps/api && $(UV) run --extra dev ruff check app/ && $(UV) run --extra dev ruff format --check app/

lint-model-collector:
	@echo "▶ lint model-collector"
	cd agents/model-collector && $(UV) run --extra dev ruff check model_collector/ && $(UV) run --extra dev ruff format --check model_collector/

lint-web:
	@echo "▶ lint web"
	cd apps/web && $(BUN) run lint --max-warnings 0

# ── Seed ───────────────────────────────────────────────────────────────────

seed:
	curl -s -X POST http://localhost:8000/api/v1/seed/demo | python3 -m json.tool

# ── Clean ──────────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .venv -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "clean done"
