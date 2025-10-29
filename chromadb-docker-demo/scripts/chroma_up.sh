#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/chroma_data"

# Crea el directorio de persistencia si no existe.
if [[ ! -d "${DATA_DIR}" ]]; then
  echo "[chroma_up] Creando directorio de datos en ${DATA_DIR}";
  mkdir -p "${DATA_DIR}"
fi

echo "[chroma_up] Iniciando servicios de ChromaDB con Docker Compose"
cd "${PROJECT_ROOT}"
docker compose up -d
