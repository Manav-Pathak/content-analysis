## BrandTrack Backend

This repo now treats Docker Compose as the primary development and deployment path.

### What runs where

- `api` is the FastAPI container exposed on `http://localhost:8000`
- `db` is the Dockerized PostgreSQL instance exposed on host port `5433`
- `pgadmin` is optional and only starts when you ask for the `tools` profile

Your existing Windows PostgreSQL on `5432` stays separate. Docker Postgres uses:

- inside Docker network: `db:5432`
- from your Windows host: `localhost:5433`

### Why this setup

This is the path that best matches eventual deployment on EC2:

- the app connects to Postgres using the Docker service name
- `docker compose up --build` boots the backend stack consistently
- Swagger UI works from the containerized API at `http://localhost:8000/docs`

### Environment variables

Primary containerized workflow:

- `DATABASE_URL=postgresql://<user>:<password>@db:5432/<db>`

Optional local FastAPI fallback:

- `LOCAL_DATABASE_URL=postgresql://<user>:<password>@localhost:5433/<db>`

If you only use Docker Compose, you do not need `LOCAL_DATABASE_URL`.

### Start the stack

1. Make sure Docker Desktop is running.
2. Create or update `.env` from `.env.example`.
3. Start the main stack:

```bash
docker compose up --build
```

4. Start pgAdmin too if you want the GUI:

```bash
docker compose --profile tools up --build
```

### What to test in Swagger

Open `http://localhost:8000/docs` and verify these in order:

1. `GET /health`
   Expected: `{"status":"ok"}`
2. `GET /health/db`
   Expected: DB connection succeeds and `users_table_present` is `true`
3. `POST /auth/register`
   Expected: new user is created
4. `POST /auth/login`
   Expected: JWT access token is returned
5. Swagger `Authorize`
   Paste `Bearer <token>` or just the token depending on the Swagger prompt
6. `GET /auth/me`
   Expected: the authenticated user is returned

### What to verify outside Swagger

- `docker compose logs api`
  The API should start without database connection errors
- `docker compose logs db`
  Postgres should report it is ready to accept connections
- optional pgAdmin at `http://localhost:5050`
  Register server with host `db`, port `5432`, and your Postgres credentials

### Current table behavior

Right now tables are auto-created on API startup through SQLAlchemy:

- [app/main.py](/mnt/d/map/app/main.py:10)

That is good enough for the first build phase. Later we should switch to Alembic migrations before deployment gets serious.
