# DIGA UI POC — Deployment Architecture Requirement

## Overview
Two-container architecture (frontend + backend) managed via Docker Compose.
No cloud-native orchestration. Designed for a closed network environment.

## Containers

### Backend
- **Image:** `docker-dev.company/python:3.12-slim`
- **Port:** 8000
- **Dependencies:** `requirements.txt` (existing, no modifications)
- **Resources:** 2 vCPU, 2 GiB RAM

### Frontend
- **Image:** `docker-dev.company/node:18-alpine`
- **Port:** 3000
- **Dependencies:** `package.json` / `package-lock.json` (existing, no modifications)
- **Resources:** 1 vCPU, 1 GiB RAM

## Configuration
A single `.env` file controls all environment-specific values:

```env
# Registry & Package Sources
DOCKER_REGISTRY=docker-dev.company
NPM_REGISTRY=https://strive.company/artifactory/npm/repos
PIP_INDEX_URL=https://strive.company/artifactory/pypi/simple

# LiteLLM
LITELLM_PROXY_URL=https://...
LITELLM_TOKEN=...
LITELLM_MODEL=...

# App
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

## Docker Compose

```yaml
version: "3.9"

services:
  backend:
    image: ${DOCKER_REGISTRY}/python:3.12-slim
    ports:
      - "${BACKEND_PORT}:8000"
    env_file: .env
    volumes:
      - ./backend:/app
    working_dir: /app
    command: >
      sh -c "pip install --index-url ${PIP_INDEX_URL} -r requirements.txt &&
             uvicorn main:app --host 0.0.0.0 --port 8000"
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2048M

  frontend:
    image: ${DOCKER_REGISTRY}/node:18-alpine
    ports:
      - "${FRONTEND_PORT}:3000"
    env_file: .env
    volumes:
      - ./frontend:/app
    working_dir: /app
    command: >
      sh -c "npm config set registry ${NPM_REGISTRY} &&
             npm install &&
             npm start"
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1024M

## Constraints
- All images must be pulled from `docker-dev.company`
- All Python packages must resolve from Artifactory PyPI proxy
- All Node packages must resolve from Artifactory npm registry
- No public internet access assumed
- Replicas: 1
- Storage: 2 GB PVC (backend), 2 GB data volume as needed
```