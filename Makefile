.PHONY: backend-venv backend-install backend-install-dev backend-run-api backend-test backend-clean
.PHONY: frontend-install frontend-dev frontend-build
.PHONY: dev run-all

VENV_DIR := .venv
PYTHON := python3
PIP := $(CURDIR)/$(VENV_DIR)/bin/pip
PY := $(CURDIR)/$(VENV_DIR)/bin/python

# Detect if frontend exists
FRONTEND_EXISTS := $(shell [ -d frontend ] && echo 1 || echo 0)

backend-venv:
	$(PYTHON) -m venv $(VENV_DIR)

backend-install: backend-venv
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

backend-install-dev: backend-venv
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements-dev.txt

backend-run-api: backend-install
	cd backend && $(PY) main.py --serve --host 0.0.0.0 --port 5000

backend-test: backend-install-dev
	cd backend && $(PY) tests/test_all.py

backend-clean:
	rm -rf $(VENV_DIR)

# Frontend targets (will work once frontend is merged)
frontend-install:
	@if [ ! -d "frontend" ]; then \
		echo "❌ Frontend directory not found. Merge frontend branch first."; \
		exit 1; \
	fi
	@if [ -f "frontend/package.json" ]; then \
		cd frontend && npm install; \
	else \
		echo "⚠️  No package.json found in frontend/"; \
	fi

frontend-dev:
	@if [ ! -d "frontend" ]; then \
		echo "❌ Frontend directory not found. Merge frontend branch first."; \
		exit 1; \
	fi
	@if [ -f "frontend/package.json" ]; then \
		cd frontend && npm run dev; \
	else \
		echo "⚠️  Serving static frontend..."; \
		cd frontend && python3 -m http.server 3000; \
	fi

frontend-build:
	@if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then \
		cd frontend && npm run build; \
	else \
		echo "❌ Frontend not available or no build script"; \
	fi

# Run full stack (backend + frontend)
dev: backend-install
	@echo "🚀 Starting full stack development servers..."
	@echo "   Backend API will run on http://localhost:5000"
	@if [ -d "frontend" ]; then \
		echo "   Frontend will run on http://localhost:3000"; \
		echo ""; \
		echo "Press Ctrl+C to stop both servers"; \
		trap 'kill 0' INT; \
		cd backend && $(PY) main.py --serve & \
		make frontend-dev & \
		wait; \
	else \
		echo "   Frontend not merged yet - running backend only"; \
		cd backend && $(PY) main.py --serve; \
	fi

run-all: dev
