## Configurations for connecting WebUI, Pipelines and Document Processor

When dockerized the document processer container and pipelines are not connected with the webui.

## Setup

Before running the services for the first time, create the shared Docker network:

```bash
docker network create app-network
```

Then start the services as required:

```bash
docker-compose -f docker-compose.webui.yml up -d
docker-compose -f docker-compose.fastapi.yml up -d
docker-compose -f docker-compose.fastapi.yml up -d
```