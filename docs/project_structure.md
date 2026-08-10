# Project Structure

```
smartcare-assets/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entrypoint
│   ├── database.py          # Async SQLAlchemy engine/session setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── asset.py         # Asset ORM model (asset_code, tracking_id, status, battery_level)
│   └── routers/
│       ├── __init__.py
│       ├── assets.py        # Asset registration and search endpoints
│       └── telemetry.py     # Battery/location telemetry ingestion endpoint
├── alembic/
│   └── versions/            # Database migration scripts
├── tests/
│   ├── __init__.py
│   └── test_health.py       # Pytest test suite
├── docs/
│   └── project_structure.md
├── .env.example              # Template for environment variables (never committed with real secrets)
├── .gitignore
├── requirements.txt
├── Dockerfile                # Container image definition for the API service
├── docker-compose.yml         # Multi-container orchestration (API + PostgreSQL)
└── README.md
```

## Purpose of Major Folders/Files

- **app/**: all application source code, organized by responsibility (routers, models, database config).
- **app/models/**: SQLAlchemy ORM classes representing database tables — kept separate from route logic
  so the data layer can be tested and reused independently.
- **app/routers/**: FastAPI routers grouped by feature area (assets, telemetry) rather than one large file,
  supporting modularity as more features (maintenance, analytics) are added.
- **alembic/**: version-controlled database schema migrations, allowing schema changes to be tracked
  and applied consistently across environments.
- **tests/**: automated test suite, mirroring the app package structure.
- **.env.example**: documents required environment variables without committing real credentials —
  actual `.env` files are excluded via `.gitignore`.
- **Dockerfile / docker-compose.yml**: containerization definitions, described in detail in Sections 7–9.
