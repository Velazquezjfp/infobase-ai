# Sprint 001 — Raw Requirements

_One bullet per requirement. Agent will ground against current state (APIs, DB, env vars) and produce polished files when you run `/requirement-polish 001`._

_Tips:_
- _Keep bullets focused — one requirement per bullet._
- _Mention specific tables, endpoints, or env vars when you know them; the agent will verify against current state._
- _For NFRs, include a measurable target (e.g., "p95 latency under 100ms") or the agent will ask._
- _To reference another requirement as a dependency, mention its full compound ID (e.g., "follows on from S041-F-003")._

<!-- Write your raw requirements below this line. -->

#fixes needed in the app. 

Summary: 
Over all description: 
This app most undergo changes for deployment in a closed private environment with no internet access. Only access to a model via LiteLLM proxy and the images and libraries in package.json and requirements.txt via artifactory, which will use env variables or variables in the docker files to build the image. Development in this machine can point to the public internet and to a LiteLLm installed locally, but simmulation should be done carefully to ensure a smooth deployment in the real cluster. For your information and context I will deploy this in a development server first where I will get to try all the urls, after that I will rceate the spec and requirement for the BDOP. 

Essentially no requirement should add new things or functionalities, its more about switching existing ones, packaging in docker the current one, 
making it 

As context it could really help this diagrams, use it appart from the instructions in your pormpt to understand how the app works: 
docs-v1/diagrams

Requirements:

1.- Docker for connection to Lite LLM simmulating proxy, use local host url pointing to LiteLLM locally, litellm locally must use Ollama internallz which is already installed in Linux. It hsould target Gemma4. This is a crucial first step and all the requirements should be developed and tested with this connection and not with current Gemini endpoint. All services currently using gemini endpoint must switch and they must be tested, but only after all functionalities have been filtered down.  

2.- Simmulate URLs and connections: 
Change gemini endpoint over internet for liteLLM proxy. LiteLLm should use locally Ollama, make sure that you can reach it, it should be installed already, if a new contaienr is necessary build it and include it in docker compose, but add a variable to use or not use/build this extra container, this is only for my own local development. There should be a URL, secret and model variabels used in LiteLLM. For Lite LLM you should install it, if that is a python library make sure to use the virtual environment present in this codebase "backend/venv" and add teh library to requirements. 

Important is also to not completely swap the gemini internet endpoint, but add a variable so I can always switch from internet to local (liteLLM proxy). 

URL for registry should be included as variable, I will point to internal artifactory once in teh server, here is okay to point to public internet or publik docker registry to download teh images. 

URL for python and node registries are also needed, again, for this demo its okay to use the public internet, but is very improtant to only use what is already in the requirements and package.json, donot add anything else unless necessary to meet requirements. 

In the second section of this requirement file I have more ddetials on this hosting requirement. 


3.- The final solution wont have internet access, so URLs present in the context navigation wont open, its important to implement this context as markdown or only as text, so when clicking in teh urls only the text shouldbe shown, and clarification should be made as well that there is no internet, but the content is being simmulated to reference successfully in the dynamic context. You may have to create another task for asub agent to collect the url, extract the html and only use text or markdown instead of the navigation, also very important to test that it effectively injects into context for the LLM on queries.  

5.- There is certain dependencies like anonymization service and open search (document search) service, this bith you will find that are external contaienrs, for now replace the functionaliity to show a message (anonymization not yet implement, same for the document search functionality), do not get rid of teh current mechanisms, simply use a variable in config file to use connections or not, at first I need tio disable them, after at some point I will actually implement them. 

6.- No document upload enable by using a variable in config file, I need to block updaloads for now. This demo should be a closed environment in version one, that means that we should block and present a message to the user if it uses the "upload" button. No new docs should be allowed.

7.- The documents in /root_docs should be allocated into folders on start, if the users logs off or closes the window/session. the app should restart, restarting means all modified docs like translations or other should be deleted, and only root_docs should be loaded again into the intial position. This requirement may change how data is persisted. I need a one shot demo, user logs in, uses the chat interface, uses buttons and commands, if it leaves the session, logs off, goes un-acttive for more than 10 minutes then teh app simply restarts. The root docs that I need are mapped below: 

Personal Data: 
root_docs/Aufenthalstitel.png
root_docs/Geburtsurkunde.jpg
root_docs/Personalausweis.png

certificates: 
root_docs/Sprachzeugnis-Zertifikat.pdf

Applications and forms: 
root_docs/Anmeldeformular.pdf

Additional information: 
root_docs/Notenspiegel.pdf

8.- All messages and implementations should be done in German first, considering that there is an option to change language, German is priority, we shouldnt implement the english version unless specified, however it has to be tested, if language is changed and there is no translations, there shouldn't be any error, simply no translation.   

9.- check conflicts and potential errors from the documented api, db and environment under teh folder /docs, some docs could point to antipatterns or redundancies, it is worth checking. Some other requirements may emerge from here.  




-----------------------------------------------
None functional/ hosting requirements. 

The points here are very important and should be a priority as well. They are referenced or are also related to some of teh requirements above. 

I will need to create 2 docker containers, one for backend and one for frontend. This app is not yet working in containers, so the goal is to have a docker compose and 2 images. Below is more technical detail and proposed content for the docker files and hosting requirements. 


The constraints part is exactly what will happen in teh official deployment, right now you dont have to check artifactory or other constraints as explained above, is only for your context of what is resired in teh final product. 

Do not take this file as official, but for guidance, use it as an example to satisfy my requirement: 
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


-----------------------------------------------------------------------

Double check your understanding: We are getting this app ready for deployment in a provate server, we are changing the architecture for a modular container based approach. 



