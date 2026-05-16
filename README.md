# BrandTrack Backend

BrandTrack is a backend service for tracking brand and product mentions across external content platforms. Users can subscribe to keywords such as `Sony Headphones`; the system stores those tracking subscriptions and is designed to ingest mentions from sources such as YouTube, Reddit, and news APIs.

The project is being built as a production-aware FastAPI backend with PostgreSQL persistence, Docker-based local infrastructure, and a planned background ingestion pipeline using Redis and Celery.

## Current Status

Implemented:

- FastAPI application with Docker Compose workflow
- PostgreSQL database container
- Optional pgAdmin container
- JWT-based authentication
- User registration, login, and protected profile endpoint
- SQLAlchemy models for users, tracked keywords, source configs, mentions, and ingestion runs
- Keyword management API
- Automatic YouTube and Reddit source config creation when a keyword is tracked

Planned:

- Redis and Celery worker setup
- Reddit ingestion through PRAW
- YouTube Data API ingestion
- Rate limiting and retry handling for external APIs
- Mention analytics endpoints
- Alembic migrations
- AWS EC2 deployment configuration

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- bcrypt password hashing
- Docker and Docker Compose

Planned additions:

- Redis
- Celery
- PRAW
- YouTube Data API client

## Architecture Overview

The backend separates API request handling, validation, business logic, and database models:

```text
Client / Swagger
  -> app/routes
      -> app/schemas
      -> app/services
          -> app/models
              -> PostgreSQL
```

The current keyword flow stores user intent only. Creating a tracked keyword does not call YouTube or Reddit immediately. Instead, it creates database records that future background workers can read when performing ingestion.

```text
User creates keyword
  -> tracked_keywords row
  -> keyword_source_configs rows for youtube and reddit
  -> future worker reads configs
  -> worker stores mentions and ingestion_runs
```

## Repository Structure

```text
app/
  main.py                 FastAPI app setup, lifespan hook, router registration
  config.py               Environment-based settings
  database.py             SQLAlchemy engine, session factory, and DB dependency

  dependencies/
    auth.py               Reusable protected-route dependency

  models/
    user.py               Users table
    tracked_keyword.py    User-owned keyword subscriptions
    keyword_source_config.py
                           Per-keyword source settings for YouTube, Reddit, news
    mention.py            Stored external mentions with raw JSONB payloads
    ingestion_run.py      Background ingestion run history and counters
    enums.py              Shared enum values

  routes/
    auth.py               Register, login, and current-user endpoints
    keywords.py           Tracked keyword endpoints

  schemas/
    user.py               Auth request and response schemas
    keyword.py            Keyword request and response schemas

  services/
    auth.py               Password hashing, JWT creation, auth helpers
    keywords.py           Keyword business logic and DB operations

docker-compose.yml        Local API, PostgreSQL, and optional pgAdmin stack
Dockerfile                FastAPI API image
requirements.txt          Runtime dependencies for Docker builds
```

## Data Model Summary

`users`

Stores user accounts and authentication data.

`tracked_keywords`

Stores the keywords a user wants to monitor. Each user can track a normalized keyword only once.

`keyword_source_configs`

Stores source-specific settings for each keyword. A keyword currently gets default configs for YouTube and Reddit.

`mentions`

Stores individual external posts, videos, comments, or articles discovered during ingestion. Raw platform responses are stored in PostgreSQL `JSONB`.

`ingestion_runs`

Stores background job metadata such as status, retry count, cursor values, item counts, and errors.

## Setup

Create a `.env` file from `.env.example` and fill in the values:

```bash
cp .env.example .env
```

Start the main stack:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

PostgreSQL runs inside Docker on `db:5432` and is exposed to the host on `localhost:5433`.

Start pgAdmin with the optional tools profile:

```bash
docker compose --profile tools up --build
```

pgAdmin will be available at:

```text
http://localhost:5050
```

When registering the database server inside pgAdmin, use:

```text
Host: db
Port: 5432
```

## API Endpoints

Health:

- `GET /health`
- `GET /health/db`

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

Keywords:

- `POST /keywords`
- `GET /keywords`
- `GET /keywords/{keyword_id}`
- `DELETE /keywords/{keyword_id}`

## Verification Flow

Open Swagger UI at `http://localhost:8000/docs` and verify:

1. `GET /health` returns `{"status": "ok"}`.
2. `GET /health/db` confirms the database connection and expected tables.
3. `POST /auth/register` creates a user.
4. `POST /auth/login` returns a JWT access token.
5. Swagger authorization works with the token.
6. `GET /auth/me` returns the authenticated user.
7. `POST /keywords` creates a tracked keyword and default YouTube/Reddit source configs.
8. `GET /keywords` returns the current user's active tracked keywords.
9. `GET /keywords/{keyword_id}` returns one tracked keyword.
10. `DELETE /keywords/{keyword_id}` deactivates a keyword.

Example keyword request:

```json
{
  "keyword": "Sony Headphones",
  "description": "Track reviews, launch chatter, and buyer sentiment."
}
```

## Development Notes

Tables are currently created on application startup with:

```python
Base.metadata.create_all(bind=engine)
```

This is useful during early development. Production schema changes should use Alembic migrations.

The API container is built from the local repository and uses Docker Compose for local development. A production deployment should remove development-only behavior, use stable image builds, and manage secrets outside committed files.
