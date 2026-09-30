# Cities API — FastAPI + PostgreSQL on Podman

A minimal FastAPI backend with a full CRUD over a `cities` table, running in
Podman containers with PostgreSQL. Built as a self-contained demo: start the
stack, open Swagger, create/read/update/delete cities.

## Prerequisites

- Podman 5.x with the Compose provider (`podman compose` delegates to
  Docker Compose v2 as an external plugin). No `podman-compose`.
- Free ports: **8000** (API). PostgreSQL's 5432 stays unpublished.
- Base images come from AWS ECR Public Gallery, so no Docker Hub account or
  rate limit is needed.

## Quick path

1. `podman compose up -d --build`
2. Open Swagger UI: <http://localhost:8000/docs>
3. `podman compose down` to stop it.

## Endpoints

| Method | Path             | Success | Errors            |
| ------ | ---------------- | ------- | ----------------- |
| POST   | `/cities`        | 201     | 409 duplicate name |
| GET    | `/cities`        | 200 list (ordered by name) | — |
| GET    | `/cities/{id}`   | 200     | 404               |
| PUT    | `/cities/{id}`   | 200     | 404, 409 name conflict with a different id |
| DELETE | `/cities/{id}`   | 204     | 404               |
| GET    | `/health`        | 200 `{"status":"ok"}` | — |
| GET    | `/`              | 200 pointer to `/docs` | — |

Name uniqueness is checked case-insensitively at the application level.

Interactive docs: Swagger UI at `/docs`, ReDoc at `/redoc`.

## Project layout

| Path                 | Role                                    |
| -------------------- | --------------------------------------- |
| `app/main.py`        | App factory, lifespan (creates tables), health route |
| `app/routers/cities.py` | CRUD routes for `cities`             |
| `app/models.py`      | SQLAlchemy 2.0 `City` model             |
| `app/schemas.py`     | Pydantic request/response schemas       |
| `app/database.py`    | Engine, session factory, `get_db`       |
| `Containerfile`      | Image build for the API                 |
| `compose.yaml`       | API + PostgreSQL stack                  |

Tables are created at startup with `Base.metadata.create_all()` — no Alembic.

## Reset the data

```bash
podman compose down -v    # stops the stack and deletes the pgdata volume
```

## Roadmap

- Deploy the same backend to Render.
