#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${PROJECT_ROOT}"
echo "[chroma_logs] Siguiendo logs de ChromaDB"
docker compose logs -f chroma
