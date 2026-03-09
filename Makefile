.PHONY: backend-venv backend-install backend-install-dev backend-run-api backend-test backend-clean

VENV_DIR := .venv
PYTHON := python3
PIP := $(VENV_DIR)/bin/pip
PY := $(VENV_DIR)/bin/python

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
