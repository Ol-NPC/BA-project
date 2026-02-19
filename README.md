# BA-project

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-success)
![Docker](https://img.shields.io/badge/Docker-Compose-informational)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-informational)
![Nginx](https://img.shields.io/badge/Nginx-reverse--proxy-lightgrey)

Backend service for lead collection with REST API, containerized deployment, and protected API documentation.

---

## Stack

- Python 3.11
- FastAPI + Uvicorn
- PostgreSQL 16
- Docker & Docker Compose
- Nginx reverse proxy
- OpenAPI / Swagger (HTTP Basic Auth)

---

## Architecture

Data flow:

Client  
↓  
Nginx (reverse proxy)  
↓  
FastAPI application (Docker container)  
↓  
PostgreSQL (Docker volume)

- Database is isolated inside Docker network
- Secrets stored in `.env`
- API documentation protected via HTTP Basic Auth

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | `/ping` | Health check |
| POST | `/leads` | Create lead |
| GET | `/leads` | List leads |
| GET | `/leads/{lead_id}` | Get lead by ID |
| GET | `/docs` | Swagger UI (protected) |

---

## Project Structure
backend/ → FastAPI application
infra/ → Docker Compose configuration & Nginx config
docs/ → Architecture documentation & deployment evidence


curl http://localhost:8001/ping

