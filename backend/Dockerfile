ARG DOCKER_REGISTRY=docker.io
FROM ${DOCKER_REGISTRY}/python:3.12-slim

ARG PIP_INDEX_URL=https://pypi.org/simple
# S001-NFR-005 closed-environment workaround:
# The internal Artifactory's TLS cert is signed by a corporate CA that the
# container's default CA bundle (Mozilla) does not trust, so plain pip TLS
# verification fails with "SSL: CERTIFICATE_VERIFY_FAILED" / similar. We mark
# the host as "trusted" for the duration of the install — equivalent to
# `npm config set strict-ssl false` in frontend/Dockerfile. Override via
# `--build-arg PIP_TRUSTED_HOST=<host>` (compose pulls from .env if needed).
# Production deployments should replace this with a CA-bundle injection
# (COPY corporate-ca.crt + REQUESTS_CA_BUNDLE / SSL_CERT_FILE env vars) and
# delete this build arg.
ARG PIP_TRUSTED_HOST=art.strive.bamf.in.bund.de
ARG BACKEND_PORT=8000

# S001-NFR-005 closed-environment workaround:
# The previous `apt-get update && apt-get install -y curl` step was used solely
# to provide curl for the runtime healthcheck. In a closed network the apt step
# fails because deb.debian.org is not resolvable and no internal apt mirror is
# configured. We removed the apt block entirely and replaced the curl-based
# healthcheck with a python3 + urllib one (Python is already in the base image).
# If/when an internal Debian mirror is wired up, this block can come back —
# along with curl — but it is not required for the runtime contract.

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /bin/sh app

WORKDIR /app

# Copy requirements separately so pip install layer is cached independently of code changes
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir \
        --trusted-host "${PIP_TRUSTED_HOST}" \
        --index-url "${PIP_INDEX_URL}" \
        -r backend/requirements.txt

COPY --chown=app:app backend/ backend/
COPY --chown=app:app ontology_shacl_material/ ontology_shacl_material/
COPY --chown=app:app root_docs/ root_docs/

# S001-NFR-005: pre-create the volume mount points with `app:app` ownership.
# Named volumes copy their seed contents from the image's path on first init,
# inheriting the directory's owner/perms. Without this step, named volumes
# default to root:root and the non-root `app` user gets PermissionError on mkdir.
RUN mkdir -p /var/app/documents \
             /app/backend/data/contexts/cases \
    && chown -R app:app /var/app /app/backend/data

ENV DOCUMENTS_PATH=/var/app/documents \
    PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO

USER app

EXPOSE $BACKEND_PORT

# S001-NFR-005 closed-environment workaround:
# Was `CMD curl -f http://localhost:8000/health` — needed curl from apt, which we removed.
# Use Python's stdlib instead: urllib.request.urlopen raises on any non-2xx response or
# connection failure, so the python3 process exits non-zero (unhealthy). 200 → exit 0
# (healthy). Same semantics as `curl -f`, no external binary required.
# NOTE: docker-compose.yml's `services.backend.healthcheck:` overrides this at runtime.
# Both files were updated to use the same python3 form for consistency.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
