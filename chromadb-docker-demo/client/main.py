"""Cliente de demostración para interactuar con ChromaDB mediante HTTP.

El script se conecta a un servidor Chroma levantado vía Docker, inserta una
colección de artículos temáticos y ejecuta consultas semánticas evaluando sus
resultados de forma heurística.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

import chromadb
from chromadb.config import Settings

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
DEFAULT_COLLECTION_NAME = "articulos"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


def load_env_file(env_path: Path) -> Dict[str, str]:
    """Carga un archivo .env simple con pares ``KEY=VALUE``."""

    if not env_path.exists():
        return {}

    env_values: Dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        env_values[key.strip()] = value.strip()
    return env_values


def resolve_setting(env_key: str, fallback: str, env_file_values: Dict[str, str]) -> str:
    """Obtiene una variable desde ``os.environ`` con respaldo al archivo .env."""

    return os.getenv(env_key) or env_file_values.get(env_key, fallback)


def build_client(host: str, port: int) -> chromadb.HttpClient:
    """Configura el cliente HTTP con telemetría desactivada y reset permitido."""

    return chromadb.HttpClient(
        host=host,
        port=port,
        settings=Settings(allow_reset=True, anonymized_telemetry=False),
    )


def ensure_documents(collection: chromadb.api.models.Collection.Collection) -> None:
    """Inserta documentos de ejemplo de manera idempotente usando ``upsert``."""

    documents: List[Tuple[str, str, Dict[str, str]]] = [
        (
            "historia-01",
            "La caída del Imperio Romano marcó el inicio de la Edad Media y transformó la política europea.",
            {"tema": "historia"},
        ),
        (
            "ia-01",
            "Los transformers revolucionaron el NLP al permitir el aprendizaje de dependencias largas en textos.",
            {"tema": "ia"},
        ),
        (
            "ecologia-01",
            "La deforestación afecta la biodiversidad y aumenta las emisiones de gases de efecto invernadero.",
            {"tema": "ecologia"},
        ),
        (
            "deporte-01",
            "El entrenamiento de resistencia mejora la capacidad aeróbica y la salud cardiovascular de los atletas.",
            {"tema": "deporte"},
        ),
        (
            "economia-01",
            "La inflación y la política monetaria están estrechamente relacionadas con las expectativas del mercado.",
            {"tema": "economia"},
        ),
        (
            "medicina-01",
            "Las vacunas de ARNm activan respuestas inmunológicas específicas con tiempos de desarrollo reducidos.",
            {"tema": "medicina"},
        ),
        (
            "tecnologia-01",
            "La computación en la nube facilita la escalabilidad de aplicaciones y la gestión de datos distribuidos.",
            {"tema": "tecnologia"},
        ),
        (
            "musica-01",
            "El jazz de los años 50 exploró la improvisación modal e influyó en generaciones posteriores de músicos.",
            {"tema": "musica"},
        ),
        (
            "literatura-01",
            "El realismo mágico en América Latina mezcló elementos fantásticos con narrativas cotidianas.",
            {"tema": "literatura"},
        ),
        (
            "ciencia-01",
            "El método científico combina observación, hipótesis, experimentación y análisis para validar teorías.",
            {"tema": "ciencia"},
        ),
    ]

    collection.upsert(
        ids=[doc_id for doc_id, _, _ in documents],
        documents=[text for _, text, _ in documents],
        metadatas=[metadata for _, _, metadata in documents],
    )


def keyword_relevance(text: str, keywords: Iterable[str]) -> int:
    """Calcula un puntaje de relevancia heurístico basado en palabras clave."""

    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw in text_lower)
    if hits == 0:
        return 0
    if hits == 1:
        return 3
    if hits == 2:
        return 4
    return 5


def evaluate_results(
    query: str,
    results: Dict[str, Sequence[Sequence]],
    keywords: Set[str],
) -> None:
    """Imprime los resultados de la consulta con evaluación heurística."""

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    print("\n==============================")
    print(f"Consulta: {query}")
    print("Resultados (top 3):")
    for idx, (doc_id, doc_text, metadata) in enumerate(zip(ids, documents, metadatas), start=1):
        score = keyword_relevance(doc_text, keywords)
        topic = metadata.get("tema", "desconocido") if isinstance(metadata, dict) else metadata
        print(f"#{idx} -> ID: {doc_id}")
        print(f"       Tema: {topic}")
        print(f"       Texto: {doc_text}")
        print(f"       Relevancia aparente (0-5): {score}")

    coverage_topics = {md.get("tema") for md in metadatas if isinstance(md, dict)}
    print(f"Cobertura temática: {', '.join(sorted(t for t in coverage_topics if t)) or 'sin datos'}")

    related_hits = [doc for doc in documents if any(kw in doc.lower() for kw in keywords)]
    if related_hits:
        print("Notas: Los resultados contienen coincidencias claras con las palabras clave.")
    else:
        print("Notas: Las coincidencias dependen de la similitud semántica, no hay palabras clave exactas.")


def run(reset: bool) -> None:
    env_file_values = load_env_file(ENV_PATH)

    host = resolve_setting("CHROMA_HOST", DEFAULT_HOST, env_file_values)
    port_str = resolve_setting("CHROMA_PORT", str(DEFAULT_PORT), env_file_values)
    try:
        port = int(port_str)
    except ValueError:
        print(f"Puerto inválido en CHROMA_PORT: {port_str}. Usando {DEFAULT_PORT}.")
        port = DEFAULT_PORT

    client = build_client(host, port)

    if reset:
        print("[cliente] --reset recibido. Limpiando datos remotos...")
        client.reset()

    collection = client.get_or_create_collection(name=DEFAULT_COLLECTION_NAME)

    ensure_documents(collection)
    print("[cliente] Documentos insertados/actualizados correctamente.")

    queries = [
        {
            "text": "¿Cómo reducir el impacto ambiental de una ciudad?",
            "keywords": {"ambiental", "deforestación", "emisiones", "biodiversidad"},
        },
        {
            "text": "¿Qué avances recientes mejoraron el procesamiento del lenguaje natural?",
            "keywords": {"nlp", "transformers", "lenguaje", "ia"},
        },
        {
            "text": "¿Qué factores explican el aumento de los precios?",
            "keywords": {"inflación", "precios", "monetaria", "economía"},
        },
    ]

    for query_data in queries:
        response = collection.query(
            query_texts=[query_data["text"]],
            n_results=3,
        )
        evaluate_results(query_data["text"], response, set(query_data["keywords"]))

    print("\nEvaluación completada. Revisa los resultados anteriores para un análisis heurístico.")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cliente HTTP para ChromaDB")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Limpia la base de datos remota antes de insertar documentos.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    arguments = parse_args(sys.argv[1:])
    try:
        run(reset=arguments.reset)
    except Exception as exc:  # noqa: BLE001 - reporte legible
        print(f"Error al ejecutar el cliente: {exc}")
        sys.exit(1)
