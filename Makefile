.PHONY: backend-venv backend-install backend-install-dev backend-run-api backend-test backend-clean
.PHONY: frontend-install frontend-dev frontend-build frontend-run
.PHONY: dev run-all

VENV_DIR := .venv

# Detect OS for cross-platform support
ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := $(CURDIR)\$(VENV_DIR)\Scripts\pip
    PY := $(CURDIR)\$(VENV_DIR)\Scripts\python
    RM_RF := rmdir /s /q
else
    PYTHON := python3
    PIP := $(CURDIR)/$(VENV_DIR)/bin/pip
    PY := $(CURDIR)/$(VENV_DIR)/bin/python
    RM_RF := rm -rf
endif

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
	$(RM_RF) $(VENV_DIR)

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm install && npm run dev

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# Run full stack (backend + frontend)
dev: backend-run-api frontend-run
	@echo "Starting full stack development servers..."
	@echo "   Backend API will run on http://localhost:5000"
	@echo "   Frontend will run on http://localhost:5173"

run-all: dev
