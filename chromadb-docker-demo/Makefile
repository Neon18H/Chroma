SHELL := /bin/bash
PROJECT_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV_DIR := $(PROJECT_ROOT)client/.venv
PYTHON := python3
PIP := $(VENV_DIR)/bin/pip
PYTHON_VENV := $(VENV_DIR)/bin/python

.PHONY: up down logs client-install client-run reset

up:
@$(PROJECT_ROOT)scripts/chroma_up.sh

down:
@$(PROJECT_ROOT)scripts/chroma_down.sh

logs:
@$(PROJECT_ROOT)scripts/chroma_logs.sh

client-install:
@test -d $(VENV_DIR) || ($(PYTHON) -m venv $(VENV_DIR))
@$(PIP) install -r $(PROJECT_ROOT)client/requirements.txt

client-run: client-install
@$(PYTHON_VENV) $(PROJECT_ROOT)client/main.py

reset:
@if [ "$(CONFIRM)" != "1" ]; then \
echo "Uso: make reset CONFIRM=1"; \
echo "Esta acción detiene los contenedores y elimina chroma_data."; \
exit 1; \
fi
@$(MAKE) down
@echo "[reset] Eliminando datos persistidos en chroma_data/"
@rm -rf $(PROJECT_ROOT)chroma_data/*
