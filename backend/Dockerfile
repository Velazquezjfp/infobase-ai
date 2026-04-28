ARG DOCKER_REGISTRY=docker.io
FROM ${DOCKER_REGISTRY}/python:3.12-slim

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG BACKEND_PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /bin/sh app

WORKDIR /app

# Copy requirements separately so pip install layer is cached independently of code changes
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir --index-url "${PIP_INDEX_URL}" -r backend/requirements.txt

COPY --chown=app:app backend/ backend/
COPY --chown=app:app ontology_shacl_material/ ontology_shacl_material/
COPY --chown=app:app root_docs/ root_docs/

ENV DOCUMENTS_PATH=/var/app/documents \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

USER app

EXPOSE $BACKEND_PORT

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
