# Implementación de ChromaDB con Docker para Base de Datos Vectorial

## ¿Qué es ChromaDB?
ChromaDB es una base de datos vectorial optimizada para almacenar embeddings y
realizar búsquedas de vecinos más cercanos (kNN) sobre ellos. Permite construir
experiencias de búsqueda semántica, chatbots que consultan documentos, sistemas
de recomendación personalizados y canalizaciones de análisis de datos que
aprovechan la similitud semántica entre textos, imágenes o cualquier representación
vectorial.

## Requisitos previos
- Docker y Docker Compose instalados.
- Python 3.10 o superior.
- La carpeta `./chroma_data` para persistencia se crea automáticamente al levantar el servicio.

## Variables de entorno
El archivo [`.env.example`](.env.example) contiene los valores por defecto del
servicio. Copia este archivo a `.env` y ajusta lo necesario:

```bash
cp .env.example .env
```

Variables incluidas:
- `CHROMA_IMAGE`: imagen de Docker a utilizar.
- `CHROMA_HOST` y `CHROMA_PORT`: host/puerto para exponer el servicio HTTP.
- `CHROMA_PERSIST_DIR`: ruta local para la persistencia.
- `CHROMA_IS_PERSISTENT`: habilita el guardado en disco.
- `CHROMA_TELEMETRY`: controla la telemetría anonimizada.

## Levantar ChromaDB
Asegúrate de tener los scripts con permisos de ejecución (`chmod +x scripts/*.sh`).

**Opción A:** usar Makefile.
```bash
make up
```

**Opción B:** usar Docker Compose directamente.
```bash
docker compose up -d
```

En Windows, si utilizas Git Bash o WSL, mantén las rutas relativas tal como `./chroma_data`
para que el volumen se monte correctamente.

## Probar el cliente Python
Instala dependencias en un entorno virtual local y ejecuta el cliente de ejemplo:

```bash
make client-install
make client-run
```

El script insertará documentos en la colección `articulos`, realizará 3 consultas
semánticas y mostrará una evaluación heurística de relevancia y cobertura para
cada una.

## Uso directo con `docker run` (opcional)
```bash
docker run -d --name chromadb \
  -p 8000:8000 \
  -v ./chroma_data:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  -e ANONYMIZED_TELEMETRY=FALSE \
  chromadb/chroma:latest
```

## Evaluación de resultados
El cliente imprime tres métricas heurísticas:
- **Relevancia aparente (0-5):** puntaje basado en coincidencias de palabras clave.
- **Cobertura temática:** cantidad de temas distintos presentes en los resultados.
- **Notas:** observaciones sobre coincidencias relevantes.

Estas métricas son aproximaciones simples. Para evaluaciones más robustas puedes
utilizar métricas como Recall@k, nDCG o revisiones manuales especializadas.

## Mantenimiento y Reseteo
- Detener servicios:
  ```bash
  make down
  ```
- Reset completo (detiene servicios y elimina `chroma_data/`):
  ```bash
  make reset CONFIRM=1
  ```

## Solución de problemas (FAQ)
- **Puerto ocupado:** modifica `CHROMA_PORT` en `.env` y reinicia el servicio.
- **Permisos en `./chroma_data`:** asegúrate de que tu usuario tenga acceso de lectura/escritura.
- **Telemetría:** desactivada por defecto (`ANONYMIZED_TELEMETRY=FALSE`).
- **Idempotencia:** el cliente usa `upsert`, puedes ejecutarlo múltiples veces sin duplicar documentos.
- **Compatibilidad:** los comandos son válidos para Docker Compose v2 (`docker compose`).

## Buenas prácticas de repositorio
- No commitees el contenido de `chroma_data/`.
- Evita agregar binarios o archivos generados; mantén solo texto/código.

`.gitignore` recomendado:
```gitignore
chroma_data/
client/.venv/
.env
__pycache__/
*.pyc
```

## Extensiones futuras
- Autenticación o control de acceso para el servicio HTTP.
- Uso de namespaces o múltiples colecciones para aislar datos.
- Integración con pipelines ETL que generen embeddings externos (OpenAI, HuggingFace, etc.).

## Comandos de prueba esperados
```bash
# 1) Levantar ChromaDB
make up
# 2) Instalar cliente
make client-install
# 3) Ejecutar consultas
make client-run
# 4) Ver logs del servidor
make logs
# 5) Bajar servicios
make down
# 6) Reset completo (borra datos)
make reset CONFIRM=1
```
