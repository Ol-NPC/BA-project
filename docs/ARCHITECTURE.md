# Architecture

**Stack:** Ubuntu VPS, Nginx reverse proxy, Docker Compose, FastAPI, PostgreSQL.

Data flow:

Client -> Nginx -> FastAPI (Docker) -> PostgreSQL (Docker volume)

Security:
- Swagger/OpenAPI protected with HTTP Basic Auth (env credentials)
- DB is isolated inside Docker network (no exposed port)
- Secrets are stored in `.env` (not committed)

